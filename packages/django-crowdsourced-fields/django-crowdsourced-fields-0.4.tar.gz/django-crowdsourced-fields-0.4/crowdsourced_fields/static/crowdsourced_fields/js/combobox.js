(function( $ ) {
    $.widget( "ui.combobox", {
        options: {
            source: []
        },

        _create: function() {
            var input,
                self = this,
                theElement = this.element.hide(),
                value = theElement.val(),
                wrapper = this.wrapper = $( "<span>" )
                    .addClass( "ui-combobox" )
                    .insertAfter( theElement );

            input = $( '<input>' )
                .appendTo( wrapper )
                .val( value )
                .addClass( "ui-state-default ui-combobox-input" )
                .autocomplete({
                    delay: 0,
                    minLength: 0,
                    source: self.options.source,
                    select: function( event, ui ) {
                        self.element.val(ui.item.label);
                        self._trigger( "selected", event, {
                            item: ui.item
                        });
                    },
                    change: function( event, ui ) {
                        self.element.val(input.val());
                        self._trigger( "changed", event, {
                            item: ui.item
                        });
                    }
                })
                .addClass( "ui-widget ui-widget-content ui-corner-left" );

            input.keyup(function(e) {
                self.element.val(input.val());
            });

            input.data( "autocomplete" )._renderItem = function( ul, item ) {
                return $( "<li></li>" )
                    .data( "item.autocomplete", item )
                    .append( "<a>" + item.label + "</a>" )
                    .appendTo( ul );
            };

            $( "<a>" )
                .attr( "tabIndex", -1 )
                .attr( "title", "Show All Items" )
                .html( '<span class="ui-button-icon-primary ui-icon ui-icon-triangle-1-s"></span><span class="ui-button-text"></span>' )
                .appendTo( wrapper )
                .removeClass( "ui-corner-all" )
                .addClass( "ui-button ui-widget ui-state-default ui-button-icon-only ui-corner-right ui-combobox-toggle" )
                .click(function() {
                    // close if already visible
                    if ( input.autocomplete( "widget" ).is( ":visible" ) ) {
                        input.autocomplete( "close" );
                        return;
                    }

                    // work around a bug (likely same cause as #5265)
                    $( this ).blur();

                    // pass empty string as value to search for, displaying all results
                    input.autocomplete( "search", "" );
                    input.focus();
                });
        },

        destroy: function() {
            this.wrapper.remove();
            this.element.show();
            $.Widget.prototype.destroy.call( this );
        }
    });
})( jQuery );
