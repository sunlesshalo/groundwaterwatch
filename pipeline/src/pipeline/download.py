"""Download a single weekly GRACE-DA NetCDF from NASA GES DISC.

Auth via ~/.netrc with an entry for urs.earthdata.nasa.gov. The user must
register at https://urs.earthdata.nasa.gov/users/new and authorize the
"NASA GESDISC DATA ARCHIVE" application before this will work.
"""

from __future__ import annotations

import netrc
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests

GES_BASE = "https://hydro1.gesdisc.eosdis.nasa.gov/data/GRACEDA/GRACEDADM_CLSM025GL_7D.3.0"
EARTHDATA_HOST = "urs.earthdata.nasa.gov"


class EarthdataSession(requests.Session):
    """Carry Basic auth across the GES DISC -> URS -> GES DISC redirect chain.

    NASA-recommended pattern; documented at
    https://urs.earthdata.nasa.gov/documentation/for_users/data_access/python.

    requests does not auto-apply .netrc credentials across cross-host redirects,
    so we read ~/.netrc once at construction and bind the credential to the
    session. rebuild_auth then strips it only when redirecting to a third-party
    host that is neither the data host nor URS.
    """

    def __init__(self):
        super().__init__()
        try:
            entry = netrc.netrc().authenticators(EARTHDATA_HOST)
        except (FileNotFoundError, netrc.NetrcParseError) as e:
            raise RuntimeError(
                f"~/.netrc missing or unparseable. Add a line:\n"
                f"  machine {EARTHDATA_HOST} login <uid> password <pw>\n"
                f"and chmod 600 ~/.netrc. Original error: {e}"
            )
        if not entry:
            raise RuntimeError(
                f"No ~/.netrc entry for {EARTHDATA_HOST}. Add a line:\n"
                f"  machine {EARTHDATA_HOST} login <uid> password <pw>"
            )
        login, _, password = entry
        self.auth = (login, password)

    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if "Authorization" not in headers:
            return
        original = urlparse(response.request.url).hostname
        redirect = urlparse(url).hostname
        if original != redirect and redirect != EARTHDATA_HOST and original != EARTHDATA_HOST:
            del headers["Authorization"]


def url_for(week_start: date) -> str:
    """GRACE-DA files are Monday-stamped. week_start must be a Monday."""
    if week_start.weekday() != 0:
        raise ValueError(f"week_start must be a Monday; got {week_start} (weekday {week_start.weekday()})")
    stamp = week_start.strftime("%Y%m%d")
    return f"{GES_BASE}/{week_start.year}/GRACEDADM_CLSM025GL_7D.A{stamp}.030.nc4"


def download(week_start: date, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    url = url_for(week_start)
    out = out_dir / Path(urlparse(url).path).name
    if out.exists() and out.stat().st_size > 0:
        return out

    with EarthdataSession() as s:
        # Session.trust_env=True (default) means requests reads ~/.netrc for auth.
        r = s.get(url, stream=True, timeout=120)
        r.raise_for_status()
        tmp = out.with_suffix(out.suffix + ".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if chunk:
                    f.write(chunk)
        tmp.rename(out)
    return out
