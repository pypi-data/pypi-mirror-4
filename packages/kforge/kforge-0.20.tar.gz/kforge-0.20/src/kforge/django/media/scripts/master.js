/* event handling and input greying code
 *+from http://www.scottandrew.com/weblog/articles/cbs-events
 *+and http://www.pledgebank.com/pb.js                       
 */
function addEvent(obj, evType, fn) {
  if (obj.addEventListener){
    obj.addEventListener(evType, fn, true);
    return true;
  } else if (obj.attachEvent){
    var r = obj.attachEvent('on'+evType, fn);
    return r;
  } else {
    /* alert('Handler not attached'); /* for dev only! */
    return false;
  }
}

function fadein(elem) {
  id = elem.id;
  for (var ii = 0; ii < greyed.length; ii++) {
    if (greyed[ii][0] == id && greyed[ii][1] == elem.value) {
      Element.removeClassName(elem, 'greyed');
      Element.addClassName(elem, 'darkened');
      elem.value = '';
    }
  }
}

function fadeout(elem) {
  id = elem.id;
  for (var ii = 0; ii < greyed.length; ii++) {
    if (greyed[ii][0] == id && elem.value == '') {
      Element.removeClassName(elem, 'darkened');
      Element.addClassName(elem, 'greyed');
      elem.value = greyed[ii][1];
    }
  }
}

function greyOutInputs() {
  if (!document) return;
  
  if (document.getElementById) {
    for (var ii = 0; ii < greyed.length; ii++) {
      elem = document.getElementById(greyed[ii][0])
      if (elem && elem.value == '') elem.value = greyed[ii][1];
      if (elem && elem.value == greyed[ii][1]) Element.addClassName(elem, 'greyed');
    }
  }

}


function checkInputLength(length_elem, replace_elem, length) {
  //alert('checking input length');
  var count = document.createTextNode(length_elem.value.length);
  replace_elem.replaceChild(count, replace_elem.firstChild);

  if(length_elem.value.length > length) {
    Element.addClassName(replace_elem, 'error-text');
  } else {
    Element.removeClassName(replace_elem, 'error-text');
  }
}

var rules = {
  'input' : function(element) {
    element.onfocus = function() {
      //alert('gained focus');
      fadein(this);
    };
    element.onblur = function() {
      //alert('lost focus');
      fadeout(this);
    };
  }//,
// not using the field length counting stuff at the moment
//  '#id_description' : function(element) {
//    element.onkeyup = function() {
//      checkInputLength(this, document.getElementById('desc_charcount'), 255);
//    };
//    element.onkeydown = function() {      
//      checkInputLength(this, document.getElementById('desc_charcount'), 255);
//    };
//  }
};
Behaviour.register(rules);

var greyed = [
//  ['loginform-username', ''],
//  ['loginform-password', 'password'],
  ['project-search-terms', 'Search terms...'],
  ['user-search-terms', 'Search terms...']
];
addEvent(window, 'load', greyOutInputs);

function checkDescriptionLength() {
  //alert('checking description length');
  if(document.getElementById('id_description') != null)
    checkInputLength(document.getElementById('id_description'), document.getElementById('desc_charcount'), 255);
}
// not using the field length counting stuff at the moment
// addEvent(window, 'load', checkDescriptionLength);


// The methods checkServiceStatus, showServiceStatusRunning, and
// showServiceStatusConfiguring are used in the service read page template.

function checkServiceStatus(serviceUri) {

    new Ajax.Request(serviceUri, {
        method:'get',
        onSuccess: function(transport){
            var isRunning = 0;
            var isConfiguring = 0;
            var response = transport.responseText || "";
            if (response) {
                var data = eval('(' + response + ')');
                if (data['status'] == 'Running') {
                    isRunning = 1;
                } else if (data['status'] == 'Configuring') {
                    isConfiguring = 1;
                }
            }
            if (isRunning == 1) {
                showServiceStatusRunning();
            } else {
                var t = setTimeout("checkServiceStatus('"+serviceUri+"')", 1000);
            }
        },
        onFailure: function(){ 
            var t = setTimeout("checkServiceStatus('"+serviceUri+"')", 1000);
        },
    });
}

function showServiceStatusRunning() {
    var statusElement = document.getElementById('servicestatus');
    statusElement.innerHTML = 'Running';
}

function showServiceStatusConfiguring(kforgeMediaUrl) {
    var statusElement = document.getElementById('servicestatus');
    statusElement.innerHTML = 'Configuring <img height="12" width="12" src="'+kforgeMediaUrl+'/images/ajax-loader.gif" alt="..." />';
}


