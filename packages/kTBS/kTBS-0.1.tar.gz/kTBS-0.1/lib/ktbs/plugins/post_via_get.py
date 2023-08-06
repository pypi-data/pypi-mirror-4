#    This file is part of KTBS <http://liris.cnrs.fr/sbt-dev/ktbs>
#    Copyright (C) 2011-2012 Pierre-Antoine Champin <pchampin@liris.cnrs.fr> /
#    Universite de Lyon <http://www.universite-lyon.fr>
#
#    KTBS is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    KTBS is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with KTBS.  If not, see <http://www.gnu.org/licenses/>.

"""
A plugin to allow POSTing obsels to a StoredTrace with a GET.

This is of course a Bad Thing™, as GET requests should be safe and idempotent.
However, this is required in some contexts
where issuing a POST request is not possible.

The protocol is to GET (trace_uri)?ctype=(content-type)&post=(payload)

"""
from ktbs.engine.trace.StoredTrace as OriginalStoredTrace

class StoredTrace(OriginalStoredTrace):
    def check_parameters(self, parameters, method):
        """I implement :meth:`~rdfrest.local.ILocalResource.check_parameters`

        I accept the "post" parameter in get_state.
        """
        if method == "get_state":
            if "post" in parameters and "ctype" in parameters \
                    and len(parameters) == 2:
                return # ok
        return super(StoredTrace, self).check_parameters(parameters, method)

    def get_state(self, parameters=None):
        """I implement :meth:`.interface.IResource.get_state`.

        If parameters contains 'ctype' and 'post', I perform a post instead.
        """


def start_plugin():
    import ktbs.service
    ktbs.service.StoredTrace = StoredTrace
