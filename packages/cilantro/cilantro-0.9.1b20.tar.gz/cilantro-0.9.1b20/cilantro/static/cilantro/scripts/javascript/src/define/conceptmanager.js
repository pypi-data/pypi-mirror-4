define(['jquery', 'cilantro/define/view'],
    function($, View) {
        /**
          Sets up and manages the view sets for each criterion option.

          On each request for a criterion option, the response returns an array
          of hashes that contain the information necessary to construct the
          content of the view. HTML forms and Charts (provided by the HighCharts
          library are considered built-in views. Custom views (for example if one
          wanted to some sort of tree-view to be selected from)
          must be handled using view-specific JS or the view-set JS.

          @class
          @author <a href="mailto:millerjm1@email.chop.edu">Jeff Miller</a>
          @param {jQuery} $container Represents the containing element which
          encapulates all loaded views
          @param {jQuery} $titleBar Represents the title bar to which the title of
          the Criterion can be set
          @param {jQuery} $tabsBar Represents the element that contains the tabs
          associated with all currently loaded views
          @param {jQuery} $contentBox Represents the content area within the
          container that the active view is displayed
          @param {jQuery} $staticBox Represents the content area within the container
          that is common to all views (displays errors and the query button)
        */

        var Manager = {};

        var $container = $('#plugin-panel'),
            $titleBar = $('#plugin-title'),
            $tabsBar = $('#plugin-tabs'),
            $contentBox = $('#plugin-dynamic-content'),
            $staticBox = $('#plugin-static-content');

        /**
          A hash with respect to criterion IDs of the objects fetched from
          the server to build the views.

          @private
          @type object
        */
        var cache = {};

        /**
          The standard template for the tab DOM elements

          @private
          @type string
        */
        var tab_tmpl = '<a class="tab" href="#"><%= this.tabname %></a> ';

        /**
          The standard template for the "Add To Query Button"

          @private
          @type string
        */
        var add_query_tmpl = [
            '<button id="add_to_query"></button>',
            '<div class="message success">Added condition</div>'
        ].join('');

        /**
          Holds the currently viewable/active concept/criterionconcept

          @private
          @type int
        */
        var activeConcept = null;

        /**
          Holds the currently viewable view of the currently active
          concept/criterionconcept

          @private
          @type object
        */
        var activeView = null;

        /**
          Holds a reference to the addQueryButton for the activeConcept.

         @private
         @type jquery object
        */
        var $addQueryButton = null;

        /**
          List of concepts currently in the users active query

          @private
          @type array
        */
        var concepts_in_query = [];

        // RegExes used by buildQuery
        var binaryFieldRe = /^(\d+)_(\d+(?:OR\d+)*)_input([01])$/;
        var fieldRe = /^(\d*)_(\d+(?:OR\d+)*)$/;
        var opRe = /^(\d*)_(\d+(?:OR\d+)*)_operator$/;
        var pkChoiceRe = /^\d+(?:OR\d+)+$/;
        var negateRe = /-/;


        // Map used to convert array operators for the null boolean type;
        var nb_plural_to_singular_map = {"in":"exact", "-in":"-exact", "exact":"exact","-exact":"-exact"};
        var nb_singular_to_plural_map = {"exact":"in", "-exact":"-in"};

        var s_to_primative_map = {"true":true, "false":false, "null":null};

         /**
           Event listener for concepts added to the users query

           @private
        */
        function conceptAddedHandler(pk) {

            if ($.inArray(pk, concepts_in_query) < 0 ) {
                concepts_in_query.push(parseInt(pk, 10));

                if (activeConcept === parseInt(pk, 10)) {
                    $addQueryButton.html('<span>Update Condition</span>');
                    $(".success", $staticBox).show();
                }
            }
        }

        /**
           Event listener for concepts removed from the users query

           @private
        */
        function conceptDeletedHandler(concept_id){
            var index = $.inArray(parseInt(concept_id, 10), concepts_in_query);

            if (index >= 0 ){
                concepts_in_query.splice(index,1);
                if (activeConcept === parseInt(concept_id, 10)){
                    $addQueryButton.html('<span class="icon plus"/> <span>Add Condition</span>');
                      $(".success", $staticBox).hide();
                }
            }
        }

        /**
          This is a utility function that looks on the current view to find the
          datatype of a given field primary k. In the future it might use the server,
          or search all cached concepts, but for now it only uses the activeView because
          it is only called from buildQuery, where the activeView is all that matters.

          @private
        */
        function getDataType(field_pk) {

            var elements = activeView.elements;
            var datatype = null;

            $.each(elements, function(index,element) {

               if (element.type === "custom") {
                    return element.datatype;
               }

               if (element.data){
                   if (element.data.pk == field_pk){
                       datatype = element.data.datatype;
                       return false;
                   }
                   // Maybe we weren't given a pk for this one
                   if (element.data.pkchoices &&
                      $.inArray(field_pk,$.map(element.data.pkchoices, function(item, index){return item[0];}))>=0){
                      datatype = element.data.datatype;
                      return false;
                   }
               } else {
                   $.each(element.fields, function(index, field){
                       if (field.pk == field_pk){
                           datatype = field.datatype;
                           return false;
                       }
                       if (field.pkchoices &&
                            $.inArray(field_pk,$.map(field.pkchoices, function(item, index){return item[0];}))>=0){
                            datatype = field.datatype;
                            return false;
                       }
                   });
                   if (datatype !== null){
                       return false;
                   }
               }
            });
            return datatype;
        }

        /**
          This function is a utility function, currently called by the AddQueryButtonHandler,
          for concepts made of built-in views, the function will be responsible
          for analyzing the current concept's datasource and creating the
          datastructure representing the proper query for the server to
          perform.

          @private
        */
        function buildQuery(ds) {
            var fields={};
            // We need to analyze the current concept and the datasource and construct
            // the proper datastructure to represent this query on the server
            // Find all the different fields and their values in this concept
            for (var item in ds){
                if (!ds.hasOwnProperty(item)) continue;
                var m = fieldRe.exec(item); // Either a choice, assertion, or boolean
                if (m){
                    if (fields.hasOwnProperty(m[2])){
                        $.extend(fields[m[2]], {val0:ds[item], val1:undefined, op:undefined});
                    }else{
                        fields[m[2]] = {val0:ds[item], val1:undefined, op:undefined};
                    }
                    continue;
                }
                m = binaryFieldRe.exec(item); // decimal oor date
                if (m) {
                    if (fields.hasOwnProperty(m[2])) {
                        fields[m[2]]['val'+m[3]] = Number(ds[item]) || ds[item];
                    }else{
                        fields[m[2]] = {val0:undefined, val1:undefined, op:undefined};
                        fields[m[2]]['val'+m[3]] = Number(ds[item]) || ds[item];
                    }
                    continue;
                }
                m = pkChoiceRe.exec(item); // field representing the field this concept needs to query against
                if (m) {
                    if (fields.hasOwnProperty(m[0])){
                        fields[m[0]]['pk'] = ds[item];
                    }else{
                        fields[m[0]] = {val0:undefined, val1:undefined, op:undefined, pk:ds[item]};
                    }
                }
            }
            for (item in ds){
                 if (!ds.hasOwnProperty(item)) continue;
                 m = opRe.exec(item);

                 // For optional fields, we may have an operator,
                 // but the value may not exist, so don't use it,
                 // however if the operator contains null (null, -null)
                 // the operator does take anything, so thats all wee need
                 if ((m) && (fields[m[2]] || ds[item].match(/null/))) {
                     if (!fields.hasOwnProperty(m[2])){
                         fields[m[2]] = {val0:undefined, val1:undefined, op:undefined};
                     }
                     fields[m[2]]['op'] = ds[item];
                 }
            }

            // We now have the ds sorted into a sensible datastructure
            // based on the fields in the concept. Construct the server
            // required datastructure
            var nodes = [];
            for (var field_id in fields) {
                var field = fields[field_id];

                // if field_id represents a pkChoiceRe, it means it holds the PK value for this field
                var variable_pk = false;
                var pkChoices = null;
                if (pkChoiceRe.exec(field_id)) {
                    pkChoices = field_id.split('OR');
                    field_id = field.pk;
                    variable_pk = true;
                }

                field_id = Number(field_id);
                if (field.val0===undefined && field.val1===undefined && field.op!==undefined){  // either "is null" or "is not null"
                     nodes.push({
                                     'operator' : field.op,
                                     'id' : field_id,
                                     'concept_id': activeConcept,
                                     'value' : true,
                                     'datatype':getDataType(field_id)
                                });
                }
                else if (field.val0!==undefined && field.val1!==undefined && field.op!==undefined) { // Decimal Binary Op
                    nodes.push({
                                    'operator' : field.op,
                                    'id' : field_id,
                                    'value' : [field.val0,field.val1],
                                    'concept_id': activeConcept,
                                    'datatype': getDataType(field_id)
                                });
                } else if (field.val0!==undefined && field.op!==undefined && !(field.val0 instanceof Array)){ // Decimal or boolean or free text
                    nodes.push({                                                      // probably not boolean though because
                                    'operator' : field.op,                            // a specific operator has been
                                    'id' : field_id,                                  // specified
                                    'value' : field.val0,
                                    'concept_id': activeConcept,
                                    'datatype': getDataType(field_id)
                                });
                } else if (field.val0!==undefined && field.val0 instanceof Array){ // String choice, boolean (usually charted), or nullboolean, or was string-list, which is an array
                    // if field.op is null, assume the query was the default, which is "in"
                    // this one is a bit special, there is no avoiding that in this situation
                    // we could be dealing with a string "choice" option, or a nullboolean
                    // nullbooleans need to have an OR'd query specifically construct for them
                    // because they cannot use the IN operator.
                    field.op = field.op !== undefined ? field.op : "in";
                    var datatype = getDataType(field_id);
                    switch (datatype) {
                        case "boolean"     :
                        case "nullboolean" : var bool_list = [];
                                             var op = nb_plural_to_singular_map[field.op];
                                             $.each(field.val0, function(index,item){
                                                    bool_list.push( {
                                                         'operator':op,
                                                         'id' : field_id,
                                                         // In case a plugin gave us strings for null, true or false, fix it
                                                         'value' : s_to_primative_map[item] !== undefined? s_to_primative_map[item]:item,
                                                         'concept_id': activeConcept,
                                                         'datatype':datatype
                                                    });
                                             });
                                             if (bool_list.length > 1){
                                             nodes.push({
                                                 'type': negateRe.test(field.op) ? "and" : "or",
                                                 'children' : bool_list,
                                                 'concept_id': activeConcept
                                             });
                                            }else{
                                                nodes.push(bool_list[0]);
                                            }
                                            break;
                                 default  :  nodes.push({
                                                    'operator' : field.op,
                                                    'id' : field_id,
                                                    'value' : field.val0,
                                                    'concept_id': activeConcept
                                             });
                                             break;
                    }
                } else if (field.val0 !== undefined && !(field.val0 instanceof Array) &&
                          field.val1 === undefined){ // boolean when operator not specified
                     nodes.push({
                                        'operator' : "exact",
                                        'id' : field_id,
                                        'value' : field.val0,
                                        'concept_id': activeConcept
                                });
                } else {
                    // Unable to determine what this field is ?
                    throw "Unable to determine field " + field + " in concept " + activeConcept;
                }

                if (variable_pk){
                    // When we get this back from the server, we will need a way to tell
                    // that the field pk was variable, and how to recreate the datastore
                    // TODO would it be better to make the form responsible for this?
                    nodes[nodes.length-1]['id_choices'] =  pkChoices;
                }
            }

            var server_query;
            if (nodes.length === 1){
                server_query = nodes[0];
            }else{
                server_query = {
                                     'type':  activeView.join_by || "and", // TODO this should be on the concept
                                     'children': nodes,
                                     'concept_id':activeConcept
                               };
            }
            return server_query;
        }

         /**
           This function takes an avocado query datastructure and
           returns a datasource object for a concept. This is recursive.

           @private
         */
         function createDSFromQuery(parameter, recurse_ds){
             var ds = recurse_ds || {};
             var field_prefix;
             var field_portion;
             if (!parameter.hasOwnProperty("type")){
                 if (parameter.hasOwnProperty("id_choices")){
                     // I don't like this because it tightly couples the
                     // implementation of forms and datasources, but its the most
                     // elegant solution I have at the moment
                     field_portion = parameter['id_choices'].join("OR");
                     ds[field_portion] = parameter.id;
                 }else{
                     // If it just does this branch of the if, it would be a lot less
                     // coupled
                     field_portion = parameter.id;
                 }

                 // determine values for this field.
                 // if the operator contains null ("isnull" or "-isnull")
                 // then there is no value. Any value in there would have been
                 // put there explicitly for the server.
                 field_prefix = parameter.concept_id+"_"+field_portion;
                 if (!parameter.operator.match(/null/)) {
                    if (parameter.datatype  in {number:1, date:1}) {
                        // make this an array either way, even if it was not a binary operator
                        var iterator = parameter.value instanceof Array ? parameter.value : [parameter.value];
                        for (var index=0; index < iterator.length; index++){
                            ds[field_prefix+"_input"+index] = iterator[index];
                        }
                    } else {
                        if (ds.hasOwnProperty(field_prefix)){
                           if (ds[field_prefix] instanceof Array) {
                               ds[field_prefix].push(parameter.value);
                           }else{
                               ds[field_prefix] = [ds[field_prefix]];
                               ds[field_prefix].push(parameter.value);
                           }
                        //  else if (parameter.datatype && parameter.datatype.indexOf("boolean")>=0){
                        //   ds[field_prefix] = [parameter.value];
                        } else {
                           // Operators containing null do not actually take a value, and in the scenario where
                           // a value is there, it was manufactured for the backend, and must be ignored
                           ds[field_prefix] = parameter.value;
                        }
                    }
                 }
                 ds[field_prefix+"_"+"operator"] = ds[field_prefix] instanceof Array && parameter.datatype && parameter.datatype.indexOf("boolean")>=0 ?
                                                   nb_singular_to_plural_map[parameter.operator] : parameter.operator;


             } else {
                $.each(parameter.children, function(index, child){
                    createDSFromQuery(child, ds);
                });
             }
             return ds;
         }

        /**
          The handler for the 'ViewReadyEvent' event

          This event is fired by a concept plugin when it is ready
          to be inserted into the DOM. $concept here should be a
          jQuery wrapped set, ready to be placed into the DOM

          @private
        */
        function viewReadyHandler(evt, view) {
            activeView.contents = view;
            // As of right now IE 7 and 8 cannot seem to properly handle
            // creating VML rotated text in an object that is not in the DOM
            // In those conditions, the chart plugin inserts the graph into the
            // DOM and sets display to 0. We detect here if the element we were
            // passed is in the DOM or not, if not we inject it. The idea is to eventually
            // when we can do this outside the dom in all browsers, to be able to do
            // this in the existing framework
            var activeViewDom = activeView.contents.dom();
            $contentBox.append(activeViewDom);
            activeViewDom.css("display","block");

            $(".chart", activeView.contents).css("display","block"); // Hack because of IE


            if (!activeView.loaded){
                // Give the view its datasource
                // This will also prevent re-populating datasources when the
                // user clicks on a criteria in the right panel but the concept
                // has been shown before.
                $(view).trigger("UpdateDSEvent", [cache[activeConcept].ds]);
                $(view).trigger("RegisterElementsEvent");
            }

            $(view).trigger("GainedFocusEvent");

            activeView.loaded = true;
         }


        /**
          The handler for the 'ShowViewEvent' event

          This event is fired by the tab bar when a new view
          is to be displayed. tabIndex correlates to the view in the
          activeConcept's views array that needs to be shown.

          @private
        */
        function showViewHandler(evt, tabIndex) {
            if (activeView !== null){
                activeView.contents.dom().css("display","none");
                $(activeView.contents).trigger("LostFocusEvent");
                activeView.contents.dom().detach();
            }

            activeView = cache[activeConcept].views[tabIndex];

            if (activeView.loaded) {
                viewReadyHandler(null, activeView.contents);
            } else {
                // We have to look at the type of view here, custom views are responsible
                // for triggering the viewReadyHandler once their code is executed,
                // built-in views will need to be taken care of code here
                var callback = null;
                activeView.concept_id = activeConcept;
                $container.fadeIn().trigger('ViewReadyEvent', [new View(activeView, cache[activeConcept].name)]);
            }
        }
        /**
             The handler for the 'ViewErrorEvent' event

             This event is fired by a concept/concept plugin when
             an unrecoveralble error has been received. The framework
             can choose to show the 'Report Error' Panel

          @private
        */

        function viewErrorHandler(evt, details) {

        }


        /**
          The handler for the 'ElementChangedEvent' event

          This event is used by concepts to notify that the user
          has changed the value of an input

          @private
       */

        function elementChangedHandler(evt, element){
            // Update the concept datastore
            var ds = cache[activeConcept].ds;
            var missing_item = false;
            // Did anything actually change?
            if (!(element.value instanceof Array) && ds[element.name] === element.value)
            {
                // item is not an array and the values are equal to each other
                return;
            }else if (element.value instanceof Array && ds[element.name] instanceof Array){
                for (var index = 0; index < element.value.length; index++){
                    if ($.inArray(element.value[index],ds[element.name])==-1){
                        // Element in one is not in the other
                        missing_item = true;
                        break;
                    }
                }
                if ((missing_item === false)&&(element.value.length == ds[element.name].length)){
                    // All elements in one are in the other, and the lists are same length
                    return;
                }
            }

            // A field is no longer in use, most likely a field was hidden due to
            // an operator change
            if (element.value === undefined){
                // Clear out this value in the datasource
                delete cache[activeConcept].ds[element.name];
            }else{
                // Update the datasource
                cache[activeConcept].ds[element.name] = element.value instanceof Array ? element.value.slice(0) : element.value;
            }
            // If other views on this concept are already instantiated
            // notify them of the change
            $.each(cache[activeConcept].views, function(index,view) {
                if (activeView !== view && view.contents) {
                    view.contents.trigger("UpdateElementEvent",[element]);
                }
            });
        }

        /**
          This function is used by the constructQueryHandler to scan
          the concept's datasource and verify is not empty and does
          not contain empty, undefined, or null objects. If using
          the built-in query contructor, the datasource must contain
          only properly named attributes.
          @private
        */

        function postViewErrorCheck(ds){
            var empty = false;
            // Is the datasource an empty object?
            if ($.isEmptyObject(ds)) {
                empty = true;
            }else{
                // Is the datasource empty except for operators?
                empty = true;
                for (var key in ds){
                    if (!ds.hasOwnProperty(key)) continue;
                    // Note, the null operators can stand on their own.
                    if (opRe.test(key)){
                        if(ds[key] && ds[key].indexOf("isnull") >= 0){
                            empty = false;
                            break;
                        }
                    } else if (pkChoiceRe.test(key) || fieldRe.test(key) || binaryFieldRe.test(key)){
                        empty = false;
                        break;
                    }
                }
            }
            if (empty) return false;

            for (var key in ds){
                if (!ds.hasOwnProperty(key)) continue;

                if ((ds[key] === undefined) || (ds[key] === "")){
                    return false;
                }
                if (($.isArray(ds[key])) && (ds[key].length === 0)){
                    return false;
                }
            }
            return true;
        }

        /**
          This is the main control function for built-in and custom views
          that will use the default query constructor. It calls the function
          to verify the datasource, then calls the query contructor, and then
          finally triggers the UpdateQueryEvent up the DOM
          @private
        */
        function constructQueryHandler(event, ds){
            var server_query;
            ds = ds || cache[activeConcept].ds;
            // Does this datasource contain valid values?
            if (!ds.custom) {
                if (!postViewErrorCheck(ds)){
                    var evt = $.Event("InvalidInputEvent");
                    evt.ephemeral = true;
                    evt.message = "No value has been specified.";
                    $(event.target).trigger(evt);
                    return false;
                }
                server_query =  buildQuery(ds);
            } else {
                server_query = ds;
            }
            App.hub.publish("UpdateQueryEvent", server_query);
            return true;
        }

        /**
          This function is the handler for the "add to query" button.
          This button appears in the static content area for all concepts,
          builtin or not. This event passes the event to the current view.
          Builtin-views will be default listen for this event and call the
          ConstructQueryEvent, which will prepare pass it along with an "UpdateQueryEvent"
          Custom plugins can either use this default behavior (which analyzes the datasource)
          to constuct the query, or they may listen for the UpdateQueryButton clicked and
          construct the query themselves and trigger UpdateQueryEvent.
          @private
        */
        function addQueryButtonHandler(event){
            $(activeView.contents).triggerHandler("UpdateQueryButtonClicked"); // This would be better if every view didn't need to handle this
        }                                                                   // it should be concept level thing.

       /**
         This function notifies the framework that the user has entered invalid input.
         The framework will only show the same error message once, and it will only show
         one error message per invalid field (the last one to be sent). By default if no
         error message is sent on the event, then a generic error message is displayed.
         If there are any error messages, the submit button will be disabled.
         If the event object has a true ephemeral property however, the error will be
         displayed for 3 seconds, and faded-out, and the button will not be disabled
         (it is expected that ephemeral events are more notifications, and that the
         code that sent it will prevent the action the error forbids.)
         @private
       */
        function badInputHandler(evt){
            evt.reason = evt.reason ? "_"+ evt.reason : "";
            var invalid_fields = cache[activeConcept].invalid_fields;
            var target_name = $(evt.target).attr("name");
            $.each(cache[activeConcept].views, function(index,view){
                   view.contents && view.contents.dom().find("[name="+target_name+"]").addClass("invalid"+evt.reason);
                   view.contents && view.contents.dom().find("[name="+target_name+"]").children().addClass("invalid"+evt.reason);
            });
            var message = evt.message ? evt.message : "This condition contains invalid input. Please correct the above invalid fields.";
            var already_displayed = false;
            $.each($staticBox.find(".error"), function(index, warning) {
                warning = $(warning);
                var rc = warning.data("ref_count");
                if (warning.text() === message) {
                    // We are already displaying this message
                    already_displayed = true;
                    if (evt.ephemeral){
                        return;
                    }
                    else if (invalid_fields[target_name+evt.reason] === undefined){
                        // This message has been displayed, but for another field, increase
                        // the reference count
                        invalid_fields[target_name+evt.reason] = warning;
                        warning.data("ref_count", rc+1);

                    } else if (warning.text() !== invalid_fields[target_name+evt.reason].text()){
                        // This field already has an error message, but it's different,
                        // swap them
                        var field_rc = invalid_fields[target_name+evt.reason].data("ref_count");
                        invalid_fields[target_name+evt.reason].data("ref_count", field_rc-1);
                        if (invalid_fields[target_name+evt.reason].data("ref_count") === 0){
                            invalid_fields[target_name+evt.reason].remove();
                        }
                        invalid_fields[target_name+evt.reason] = warning;
                        warning.data("ref_count", rc+1);
                    }
                }
            });
            if (already_displayed) {
                return;
            }

            var warning = $('<div class="message error">'+message+'</div>');
            warning.data('ref_count',1);
            if (!evt.ephemeral){
                invalid_fields[target_name+evt.reason] = warning;
            }
            $staticBox.prepend(warning);
            // if the warning is ephemeral (meaning its should be flashed on
            // screen, but not kept there until a specific thing is fixed)
            // then fade out and then remove
            if (evt.ephemeral){
                var delay;
                if ((delay = parseInt(evt.ephemeral, 10)) === NaN) {
                    delay = 1000;
                }
                setTimeout(function() {
                    warning.fadeOut(3000, function(){
                        warning.remove();
                    });
                }, delay);
            }else{
                // if not ephemeral, disable the button
                $staticBox.find("#add_to_query").attr("disabled","true");
            }
        }

        /**
          This function notifies the framework that the user corrected an invalid field.
          The framework will only show the same error message once, and it will only show
          one error message per invalid field (the last one to be sent). By default if no
          error message is sent on the event, then a generic error message is displayed.
          If there are any error messages, the submit button will be disabled.
          @private
        */
        function fixedInputHandler(evt){
            evt.reason = evt.reason ? "_"+ evt.reason : "";
            var invalid_fields = cache[activeConcept].invalid_fields;
            var target_name = $(evt.target).attr("name");
            $.each(cache[activeConcept].views, function(index,view){
                view.contents && view.contents.dom().find("[name="+target_name+"]").removeClass("invalid"+evt.reason);
                view.contents && view.contents.dom().find("[name="+target_name+"]").children().removeClass("invalid"+evt.reason);
            });
            var rc = invalid_fields[target_name+evt.reason].data('ref_count') - 1;
            if (rc === 0){
                invalid_fields[target_name+evt.reason].remove();
            }else{
                invalid_fields[target_name+evt.reason].data('ref_count',rc);
            }
            delete cache[activeConcept].invalid_fields[target_name+evt.reason];

            // Re-enable the button if there are no more errors.
            if ($.isEmptyObject(cache[activeConcept].invalid_fields)){
                $staticBox.find("#add_to_query").removeAttr("disabled");
            }
        }

        App.hub.subscribe("ConceptAddedEvent", conceptAddedHandler);
        App.hub.subscribe("ConceptDeletedEvent", conceptDeletedHandler);
        // Bind all framework events to their handler
        $container.bind({
            'ViewReadyEvent': viewReadyHandler,
            'ViewErrorEvent': viewErrorHandler,
            'ShowViewEvent': showViewHandler,
            'ElementChangedEvent' : elementChangedHandler,
            'UpdateQueryButtonClicked' : addQueryButtonHandler,
            'InvalidInputEvent' : badInputHandler,
            'InputCorrectedEvent': fixedInputHandler,
            'ConstructQueryEvent': constructQueryHandler,
        });


        /**
          This function loads dependencies for the concept and for the any views.
          A callback does not have to be specified if the view is custom because
          the view code is responsible for firing the ViewReadyEvent.
          @private
        */
        function loadDependencies(deps, cb) {
            cb = cb || function(){};

            if (deps.css){
                View.loadCss(deps.css);
            }

            if (deps.js) {
                 require([deps.js], function (plugin) {
                     cb(deps);
                 });
            } else {
                cb(deps);
            }
        };

        /**
          This function handles all the administration of laoding a new concept.
          It registers with the fraemwork, sets some flags, prepares the
          "add to query" button and displays the first view
          @private
        */

        function loadConcept(concept){;
            // If we got here, the globals for the current concept have been loaded
            // We will register it in our cache
            concept = register(concept);
            activeConcept = parseInt(concept.id, 10);
            // Mark this concept as having its global dependencies loaded
            concept.globalsLoaded = true;

            // Setup tabs objects and trigger viewing of the first one
            if (concept.views.length < 2) {
                $tabsBar.hide();
            } else {
                $tabsBar.show();
            }

            var tabs = $.jqote(tab_tmpl, concept.views);
            $tabsBar.html(tabs);
            if (concept['static']){
                $staticBox.append(concept['static']);
                $addQueryButton = $staticBox.find("#add_to_query");

            }else{
                // Prepare the static concept box
                $staticBox.append(add_query_tmpl);
                $addQueryButton = $staticBox.find("#add_to_query");
                $addQueryButton.click(function(){
                     var event = $.Event("UpdateQueryButtonClicked");
                     $(this).trigger(event);
                     return false;
                });
            }
            // Make sure the button for this concept has the correct label
            if ($.inArray(activeConcept, concepts_in_query) >= 0) {
                $addQueryButton.html('<span class="icon refresh"/> <span>Update Condition</span>');
                $(".success",$staticBox).show();

            }else{
                $addQueryButton.html('<span class="icon plus"/> <span>Add Condition</span>');
                 $(".success",$staticBox).hide();
            }
            // Regardless of whether the tabs are visible, load the first view
            $tabsBar.children(':first').click();
        };

        /**
          Set up the tabs bar for the plugin, we are using the live events to automatically
          create tabs for any <a> elements put into the target area.
          Clicking a tab, will fire a ConceptTabClickEvent, which will be caught by
          tabClickedHandler. This will fire a 'ShowViewEvent' up the DOM to our listener

          @private
        */
        function tabClickedHandler(evt, tab){
            var index = $tabsBar.children().index(tab);
            $tabsBar.trigger('ShowViewEvent', index);
        };
        $tabsBar.bind('ConceptTabClickedEvent', tabClickedHandler);

        $tabsBar.tabs(true, function(evt, $tab) {
            $tab.trigger('ConceptTabClickedEvent',$tab);
        });



        /**
          Registers a concept. This creates the concept object in the
          framework cache and verifies it has all necessary properties.
          @private
        */
        function register(concept) {
            if (cache[concept.id] === undefined){
                cache[concept.id] = concept;
            }else{
                $.extend(cache[concept.id], concept);
                concept = cache[concept.id];
            }
            // Create a datasource for this concept if we don't have one
            if (!concept.ds){
                // If this concept already has a query associated with it,
                // populate the datasource
                if (concept.query) {
                    // For custom data sources, leave the query as-is
                    if (concept.query.custom) {
                        concept.ds = concept.query;
                    } else {
                        concept.ds = createDSFromQuery(concept.query);
                    }
                } else {
                    // create empty datasource
                    concept.ds = {};
                }
            }
            // Add a spot to store invalid fields.
            if (!concept.invalid_fields){
                concept.invalid_fields = {};
            }
            return concept;
        };

        // PUBLIC METHODS
        /**
           Loads and makes a particular concept active and viewable
           @public
        */
        function show(concept, existing_query, index, target) {
            $container.fadeIn();
           // Verify that we need to do anything.
           if (parseInt(concept.id, 10) === activeConcept)
               return;

           // If we already have a query for this concept, set it
           // on the concept
           if (existing_query) {
               concept.query = existing_query;
           }

           // If there is concept being displayed, save its static
           // content
           if (activeConcept !== null){
               cache[activeConcept]['static'] = $staticBox.children().detach();
           }
           // Set the name of the concept in the title bar
           // $titleBar.text(concept.name);
           if (cache[concept.id] && cache[concept.id].globalsLoaded){
                loadConcept(concept);
           } else {
                loadDependencies(concept, loadConcept);
            }
       }

        // Manager public methods
        return {
            show: show,
            isConceptLoaded: function(concept_id) {
                return (concept_id in cache);
            },
            buildQuery: buildQuery,
            constructQueryHandler: constructQueryHandler
        };
    }
);
