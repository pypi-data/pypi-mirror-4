var ui_dragging = false;


function setHeightOfEmptyDropZone(){
    //set height of empty dropzones
    var sl_slots = jq('.simplelayout-content [id*=slot]');
    // In case of only one slot, remove emptymarker klass
    if (sl_slots.length === 1){
        sl_slots.removeClass('emptymarker');
        return;
    }


    sl_slots.each(function(i, o){
        var $slot = jq(o);
        if ($slot.children('.BlockOverallWrapper:not(.ui-sortable-helper)').length === 0){
            $slot.addClass('emptymarker');
        }else{
            $slot.removeClass('emptymarker');
        }
    });
}


function refreshSimplelayoutDragndropOrdering() {

    var sl_content = jq('.simplelayout-content');
    var slots = jq('.simplelayout-content [id*=slot]');

    jq('.simplelayout-content [id*=slot]').sortable({
		items: '.BlockOverallWrapper',
        handle: jq('.BlockOverallWrapper .sl-controls .document-action-dragme'),
        scroll : true,
		forcePlaceholderSize : false,
		placeholder: 'placeholder',
        connectWith: jq('.simplelayout-content [id*=slot]'),
        /* appendTo : '.BlockOverallWrapper',*/
		opacity: 0.5,
		tolerance:'pointer',
		start: function(e,ui) {
            ui_dragging = true;
            ui.placeholder.css("width", ui.item.width()-1);
            ui.placeholder.css("height", ui.item.height()-1);
            simplelayout.toggleEditMode(enable=false, ui.item.find('.sl-controls'));
            slots.addClass('highlightBorder');

		},
        change: function(e, ui){
            setHeightOfEmptyDropZone();
        },
		update: function(e, ui){
            var ids = new Array();
            jq('.BlockOverallWrapper').each(function(i, o) { ids.push(o.id); });
            ids = ids.join(',');
            var slot = jq(e.target).attr('id');
            var column = jq(e.target).attr('class');

            var obj_uid = jq(ui.item[0]).attr('id');
            var activeLayout = jq('.sl-layout.active',ui.item);

            //jq.post('sl_dnd_saveorder', { uids : ids ,slot:slot,column:column,obj_uid:obj_uid});
            //refresh paragraph after reordering
            ajaxManager.add({url:'sl_dnd_saveorder',
                            type:'POST',
                            data:{ uids : ids ,slot:slot,column:column,obj_uid:obj_uid},
                            success:function(){
                                if (activeLayout.length !== 0){
                                    simplelayout.refreshParagraph(activeLayout[0]);
                                    }
                                }
                            });

		},
		stop: function(e, ui){
            ui.item.removeAttr("style");
            simplelayout.toggleEditMode(enable=true, ui.item.find('.sl-controls'));
            setHeightOfEmptyDropZone();
            slots.removeClass('highlightBorder');
            jq(".simplelayout-content").trigger('afterReorder');

		}

    });

    sl_content.bind("toggleeditmode", function(e){
        sl_content.sortable('enable');
    });
}

jq(refreshSimplelayoutDragndropOrdering);
