"""
This file is part of Ojota.

    Ojota is free software: you can redistribute it and/or modify
    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Ojota is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU  Lesser General Public License
    along with Ojota.  If not, see <http://www.gnu.org/licenses/>.
"""

from __init__ import run
from ojota import set_data_source

import ojota.examples.examples as pkg

def candidato_list(field, item):
    required = field in item.required_fields
    lista_cand = getattr(item, field)
    value = ""
    for element in lista_cand:
        value += '<a href="/Candidatos/%s">%s</a> ' % (element, element)

    related = False

    return (field, value, required, related)

if __name__ == '__main__':
    #renderers = [('Lista', 'cod_candidatos', candidato_list)]
    run(pkg)