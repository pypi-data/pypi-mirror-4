# Copyright (c) 2009, 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import time
from render_appointment import render_appointment, render_resource
from render_project     import render_project
from render_contact     import render_contact
#from render_document    import render_document
from render_enterprise  import render_enterprise
from render_team        import render_team
from render_task        import render_task
from render_lock        import render_lock
from render_blob        import render_folder, render_file
from render_route       import render_route
from render_process     import render_process
from render_collection  import render_collection
from coils.core         import BundleManager, CoilsException

class Render:
    @staticmethod
    def Result(entity, detail, ctx):
        result = Render.Results( [ entity ], detail, ctx)
        if (len(result) == 0):
            return None
        return result[0]

    @staticmethod
    def Results(entities, detail, ctx):
        
        if (len(entities) == 0):
            return []
            
        start = time.time()
        kinds = ctx.type_manager.group_by_type(objects=entities)
        fav_ids = { }
        results = [ ]
        
        for kind in kinds.keys():
            
            # Get favorites for this kind
            fav_ids =  ctx.get_favorited_ids_for_kind(kind, refresh=False)
            if not fav_ids:
                # this default may not be defined for this user, but we did check for it
                # so in this case we assume the context has no favorites
                fav_ids = [ ]
            
            # This list will contain (entity, representation) tuples
            e_o_list = [ ]
            
            # Render the entities
            for entity in kinds[kind]:
                method = '_render_{0}'.format(kind.lower())
                if (hasattr(Render, method)):
                    o_rep = getattr(Render, method)(entity, detail, ctx, favorite_ids=fav_ids)
                    e_o_list.append( ( entity, o_rep ) )
                else:
                    raise CoilsException('Omphalos cannot render entity {0}'.format(kind))
                    
            # Process *content* plugins if detail level 8192 is specified
            if (detail & 8192):
                plugins = BundleManager.get_content_plugins(kind, ctx)
                for e_o in e_o_list:
                    plugin_data = [ ]
                    for plugin in plugins:
                        if (hasattr(plugin, 'get_extra_content')):
                            data = plugin.get_extra_content(e_o[0])
                            if (data is not None):
                                data.update( { 'entityName': 'PluginData',
                                               'pluginName': plugin.__pluginName__ } )
                            plugin_data.append(data)
                    e_o[1]['_PLUGINDATA'] = plugin_data
                    
            results.extend(e_o_list)
            
        return [ z[1] for z in results ]

    @staticmethod
    def _render_appointment(entity, detail, ctx, favorite_ids=None):
        return render_appointment(entity, detail, ctx)

    @staticmethod
    def _render_contact(entity, detail, ctx, favorite_ids=None):
        return render_contact(entity, detail, ctx, favorite_ids=None)

    @staticmethod
    def _render_document(entity, detail, ctx, favorite_ids=None):
        return render_file(entity, detail, ctx, favorite_ids=None)

    @staticmethod
    def _render_enterprise(entity, detail, ctx, favorite_ids=None):
        return render_enterprise(entity, detail, ctx)

    @staticmethod
    def _render_file(entity, detail, ctx, favorite_ids=None):
        return render_file(entity, detail, ctx)

    @staticmethod
    def _render_folder(entity, detail, ctx, favorite_ids=None):
        return render_folder(entity, detail, ctx)

    @staticmethod
    def _render_lock(entity, detail, ctx, favorite_ids=None):
        return render_lock(entity, detail, ctx)

    @staticmethod
    def _render_project(entity, detail, ctx, favorite_ids=None):
        return  render_project(entity, detail, ctx)

    @staticmethod
    def _render_resource(entity, detail, ctx, favorite_ids=None):
        return  render_resource(entity, detail, ctx)

    @staticmethod
    def _render_task(entity, detail, ctx, favorite_ids=None):
        return render_task(entity, detail, ctx)

    @staticmethod
    def _render_team(entity, detail, ctx, favorite_ids=None):
        return render_team(entity, detail, ctx)

    @staticmethod
    def _render_process(entity, detail, ctx, favorite_ids=None):
        return render_process(entity, detail, ctx)

    @staticmethod
    def _render_route(entity, detail, ctx, favorite_ids=None):
        return render_route(entity, detail, ctx)

    @staticmethod
    def _render_collection(entity, detail, ctx, favorite_ids=None):
        return render_collection(entity, detail, ctx)
