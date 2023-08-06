cw.cubes.queueing = new Namespace('cw.cubes.queueing');

jQuery.extend(cw.cubes.queueing, {
    onUpdateSortableResourceQueue: function(event, ui){
        var resourceQueue = this.id.split('-')[1];
        var queuedEntity = ui.item.context.id.split('-')[1];
        var moveToIndex = ui.item.index();
        
        asyncRemoteExec('move_queued_entity', resourceQueue, queuedEntity, moveToIndex);
    }
});
