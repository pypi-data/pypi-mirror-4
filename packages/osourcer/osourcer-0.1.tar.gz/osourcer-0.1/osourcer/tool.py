# Copyright 2013 Daniel Narvaez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import datetime
import fnmatch
import os

_lgplv3 = {}

_lgplv3["header_html"] = """\
<!--
  - Copyright © %(year)s %(name)s
  -
  - This file is part of %(project)s.
  -
  - %(project)s is free software: you can redistribute it and/or modify
  - it under the terms of the GNU Lesser General Public License as published by
  - the Free Software Foundation, either version 3 of the License, or
  - (at your option) any later version.
  -
  - This program is distributed in the hope that it will be useful,
  - but WITHOUT ANY WARRANTY; without even the implied warranty of
  - MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  - GNU General Public License for more details.
  -
  - You should have received a copy of the GNU General Public License
  - along with this program.  If not, see <http://www.gnu.org/licenses/>.
  -->"""

_lgplv3["header_js"] = """\
/*
 * Copyright © %(year)s %(name)s
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */"""

_lgplv3["header_python"] = """\
# Copyright © %(year)s %(name)s
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>."""

_gplv3 = {}

_gplv3["header_html"] = """\
<!--
   - Copyright © %(year)s %(name)s
   -
   - This file is part of %(project)s.
   -
   - %(project)s is free software: you can redistribute it and/or modify
   - it under the terms of the GNU General Public License as published by
   - the Free Software Foundation, either version 3 of the License, or
   - (at your option) any later version.
   -
   - This program is distributed in the hope that it will be useful,
   - but WITHOUT ANY WARRANTY; without even the implied warranty of
   - MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   - GNU General Public License for more details.
   -
   - You should have received a copy of the GNU General Public License
   - along with this program.  If not, see <http://www.gnu.org/licenses/>.
  -->"""

_gplv3["header_js"] = """\
/*
 * Copyright © %(year)s %(name)s
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */"""

_gplv3["header_python"] = """\
# Copyright © %(year)s %(name)s
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>."""


def _add_header(code, header, is_html):
    if is_html:
        doctype = "<!DOCTYPE html>"

        index = code.find(doctype)
        index += len(doctype)

        code = code[:index] + "\n" + header + code[index:]
    else:
        code = header + "\n\n" + code

    return code


def _cmd_add_headers(args):
    licenses = {"gplv3": _gplv3,
                "lgplv3": _lgplv3}

    license_info = licenses[args.license]

    for dirpath, dirnames, filenames in os.walk(args.path):
        for filename in filenames:
            is_html = False
            header_template = None
            if fnmatch.fnmatch(filename, "*.py"):
                header_template = license_info["header_python"]
            if fnmatch.fnmatch(filename, "*.js"):
                header_template = license_info["header_js"]
            if fnmatch.fnmatch(filename, "*.css"):
                header_template = license_info["header_js"]
            if fnmatch.fnmatch(filename, "*.html"):
                is_html = True
                header_template = license_info["header_html"]

            if header_template:
                year = datetime.datetime.now().year
                header = header_template % {"year": year,
                                            "name": args.copyright,
                                            "project": args.project}

                path = os.path.join(dirpath, filename)

                with open(path) as f:
                    code = _add_header(f.read(), header, is_html)
                    with open(path, "w") as f:
                        f.write(code)


def _main():
    parser = argparse.ArgumentParser(description="Update license headers")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add-headers",
                                       help="add headers to source files")
    add_parser.add_argument("path", help="the source code path")
    add_parser.add_argument("--copyright", default="[NAME]",
                            help="the name of the owner")
    add_parser.add_argument("--project", required=True,
                            help="the name of the projec.")
    add_parser.add_argument("--license", choices=["gplv3", "lgplv3"],
                            required=True, help="the license to use")
    add_parser.set_defaults(func=_cmd_add_headers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    _main()
