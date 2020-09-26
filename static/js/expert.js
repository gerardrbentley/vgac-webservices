/*
─────────────────────────────────────────────────────────────
─██████████████─██████████████─████████████───██████████████─
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░████─██░░░░░░░░░░██─
─██████░░██████─██░░██████░░██─██░░████░░░░██─██░░██████░░██─
─────██░░██─────██░░██──██░░██─██░░██──██░░██─██░░██──██░░██─
─────██░░██─────██░░██──██░░██─██░░██──██░░██─██░░██──██░░██─
─────██░░██─────██░░██──██░░██─██░░██──██░░██─██░░██──██░░██─
─────██░░██─────██░░██──██░░██─██░░██──██░░██─██░░██──██░░██─
─────██░░██─────██░░██──██░░██─██░░██──██░░██─██░░██──██░░██─
─────██░░██─────██░░██████░░██─██░░████░░░░██─██░░██████░░██─
─────██░░██─────██░░░░░░░░░░██─██░░░░░░░░████─██░░░░░░░░░░██─
─────██████─────██████████████─████████████───██████████████─
─────────────────────────────────────────────────────────────
*/
// located in /txt/todo list
//second week of november - tagging event
//prevent mouse or trap mouse css
//TODO: 24/10/19: event called oncontext menu -> capture on canvas element; check riot
//TODO: 17/10/19: make image bigger on hover DONE: change colors of drawing
//DONE: 17/10/19: erase on rightclick, make reset go back to last state of current texture
//DONE: 15/10/19: make draw with mouse on affordances images: one click draw white other click draw black
//DONE: 7/12/19: after json ready: url with post -> browser sending data to the server (look at riot screenshot), then reload the page to renew json or use ajax get more json
//DONE: 30/09/19: generate a json (object?) without pictures but same texture_num + solid = 0; movable = 1; etc... + no locations either + also nine black-white imahges when user is done also... image ID + tagger ID and ... upload(post) this whole file to URL/server


// Decides if we're on staging site or live by checking for /staging/ at beginning of URL
const baseURL = window.location
const basePathArray = baseURL.pathname.split('/')
var BASE_URL = ''
if (basePathArray[1] === 'staging'){
     console.log('staging site base url')
     BASE_URL = '/staging'
}
else{
     console.log('live site url')
}

// Gets the tagger id from query string param (in url anything after ? -> ?tagger=xyz)
const queryString = window.location.search
const urlParams = new URLSearchParams(queryString)
var TAGGER_ID = 'no-tagger'
if (urlParams.has('tagger')){
    TAGGER_ID = urlParams.get('tagger')
    console.log('tagger id got from url')
}
else {
    console.log('no tagger id in url')
}

/*
────────────────────────────────────────────────────────────────────────────────────────────────────────────────
─██████████████─██████████████─████████████████──────██████████████─██████████─██████─────────██████████████────
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░░░██──────██░░░░░░░░░░██─██░░░░░░██─██░░██─────────██░░░░░░░░░░██────
─██░░██████████─██░░██████░░██─██░░████████░░██──────██████░░██████─████░░████─██░░██─────────██░░██████████────
─██░░██─────────██░░██──██░░██─██░░██────██░░██──────────██░░██───────██░░██───██░░██─────────██░░██────────────
─██░░██████████─██░░██──██░░██─██░░████████░░██──────────██░░██───────██░░██───██░░██─────────██░░██████████────
─██░░░░░░░░░░██─██░░██──██░░██─██░░░░░░░░░░░░██──────────██░░██───────██░░██───██░░██─────────██░░░░░░░░░░██────
─██░░██████████─██░░██──██░░██─██░░██████░░████──────────██░░██───────██░░██───██░░██─────────██░░██████████────
─██░░██─────────██░░██──██░░██─██░░██──██░░██────────────██░░██───────██░░██───██░░██─────────██░░██────────────
─██░░██─────────██░░██████░░██─██░░██──██░░██████────────██░░██─────████░░████─██░░██████████─██░░██████████────
─██░░██─────────██░░░░░░░░░░██─██░░██──██░░░░░░██────────██░░██─────██░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██────
─██████─────────██████████████─██████──██████████────────██████─────██████████─██████████████─██████████████────
────────────────────────────────────────────────────────────────────────────────────────────────────────────────
───────────────────────────────────────────────────────────────────────────────────────────────────
─██████████████─██████──██████─██████████████─██████──────────██████─██████████████─██████████████─
─██░░░░░░░░░░██─██░░██──██░░██─██░░░░░░░░░░██─██░░██████████──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██████████─██░░██──██░░██─██░░██████░░██─██░░░░░░░░░░██──██░░██─██░░██████████─██░░██████████─
─██░░██─────────██░░██──██░░██─██░░██──██░░██─██░░██████░░██──██░░██─██░░██─────────██░░██─────────
─██░░██─────────██░░██████░░██─██░░██████░░██─██░░██──██░░██──██░░██─██░░██─────────██░░██████████─
─██░░██─────────██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██░░██──██░░██─██░░██──██████─██░░░░░░░░░░██─
─██░░██─────────██░░██████░░██─██░░██████░░██─██░░██──██░░██──██░░██─██░░██──██░░██─██░░██████████─
─██░░██─────────██░░██──██░░██─██░░██──██░░██─██░░██──██░░██████░░██─██░░██──██░░██─██░░██─────────
─██░░██████████─██░░██──██░░██─██░░██──██░░██─██░░██──██░░░░░░░░░░██─██░░██████░░██─██░░██████████─
─██░░░░░░░░░░██─██░░██──██░░██─██░░██──██░░██─██░░██──██████████░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██████████████─██████──██████─██████──██████─██████──────────██████─██████████████─██████████████─
───────────────────────────────────────────────────────────────────────────────────────────────────*/


//__________________________________________________________________________________

var texture = document.getElementById("texture");
var canvas_draw = document.getElementById("myCanvas");

const GRID_SIZE = 8;
//__________________________________________________________________________________
/*
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
─██████████████─██████████─██████──────────██████─██████──██████─██████─────────██████████████─██████████████─██████████████─
─██░░░░░░░░░░██─██░░░░░░██─██░░██████████████░░██─██░░██──██░░██─██░░██─────────██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██████████─████░░████─██░░░░░░░░░░░░░░░░░░██─██░░██──██░░██─██░░██─────────██░░██████░░██─██████░░██████─██░░██████████─
─██░░██───────────██░░██───██░░██████░░██████░░██─██░░██──██░░██─██░░██─────────██░░██──██░░██─────██░░██─────██░░██─────────
─██░░██████████───██░░██───██░░██──██░░██──██░░██─██░░██──██░░██─██░░██─────────██░░██████░░██─────██░░██─────██░░██████████─
─██░░░░░░░░░░██───██░░██───██░░██──██░░██──██░░██─██░░██──██░░██─██░░██─────────██░░░░░░░░░░██─────██░░██─────██░░░░░░░░░░██─
─██████████░░██───██░░██───██░░██──██████──██░░██─██░░██──██░░██─██░░██─────────██░░██████░░██─────██░░██─────██░░██████████─
─────────██░░██───██░░██───██░░██──────────██░░██─██░░██──██░░██─██░░██─────────██░░██──██░░██─────██░░██─────██░░██─────────
─██████████░░██─████░░████─██░░██──────────██░░██─██░░██████░░██─██░░██████████─██░░██──██░░██─────██░░██─────██░░██████████─
─██░░░░░░░░░░██─██░░░░░░██─██░░██──────────██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██░░██─────██░░██─────██░░░░░░░░░░██─
─██████████████─██████████─██████──────────██████─██████████████─██████████████─██████──██████─────██████─────██████████████─
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
─██████──████████─██████████████─████████──████████─██████████████───██████████████─██████████████─████████████████───████████████───
─██░░██──██░░░░██─██░░░░░░░░░░██─██░░░░██──██░░░░██─██░░░░░░░░░░██───██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░░░██───██░░░░░░░░████─
─██░░██──██░░████─██░░██████████─████░░██──██░░████─██░░██████░░██───██░░██████░░██─██░░██████░░██─██░░████████░░██───██░░████░░░░██─
─██░░██──██░░██───██░░██───────────██░░░░██░░░░██───██░░██──██░░██───██░░██──██░░██─██░░██──██░░██─██░░██────██░░██───██░░██──██░░██─
─██░░██████░░██───██░░██████████───████░░░░░░████───██░░██████░░████─██░░██──██░░██─██░░██████░░██─██░░████████░░██───██░░██──██░░██─
─██░░░░░░░░░░██───██░░░░░░░░░░██─────████░░████─────██░░░░░░░░░░░░██─██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░░░██───██░░██──██░░██─
─██░░██████░░██───██░░██████████───────██░░██───────██░░████████░░██─██░░██──██░░██─██░░██████░░██─██░░██████░░████───██░░██──██░░██─
─██░░██──██░░██───██░░██───────────────██░░██───────██░░██────██░░██─██░░██──██░░██─██░░██──██░░██─██░░██──██░░██─────██░░██──██░░██─
─██░░██──██░░████─██░░██████████───────██░░██───────██░░████████░░██─██░░██████░░██─██░░██──██░░██─██░░██──██░░██████─██░░████░░░░██─
─██░░██──██░░░░██─██░░░░░░░░░░██───────██░░██───────██░░░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██░░██─██░░██──██░░░░░░██─██░░░░░░░░████─
─██████──████████─██████████████───────██████───────████████████████─██████████████─██████──██████─██████──██████████─████████████───
────────────────────────────────────────────────────────────────────────────────
─██████████████─████████████████───██████████████─██████████████─██████████████─
─██░░░░░░░░░░██─██░░░░░░░░░░░░██───██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██████░░██─██░░████████░░██───██░░██████████─██░░██████████─██░░██████████─
─██░░██──██░░██─██░░██────██░░██───██░░██─────────██░░██─────────██░░██─────────
─██░░██████░░██─██░░████████░░██───██░░██████████─██░░██████████─██░░██████████─
─██░░░░░░░░░░██─██░░░░░░░░░░░░██───██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██████████─██░░██████░░████───██░░██████████─██████████░░██─██████████░░██─
─██░░██─────────██░░██──██░░██─────██░░██─────────────────██░░██─────────██░░██─
─██░░██─────────██░░██──██░░██████─██░░██████████─██████████░░██─██████████░░██─
─██░░██─────────██░░██──██░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██████─────────██████──██████████─██████████████─██████████████─██████████████─
────────────────────────────────────────────────────────────────────────────────




*/
//__________________________________________________________________________________
function simulate(el, keyCode, key)
{
    let evtDown = new KeyboardEvent('keydown',
    {
        keyCode: keyCode,
        which: keyCode,
        code: key,
        key: key,
        bubbles: true
    })
    el.dispatchEvent(evtDown)
    let evtPress = new KeyboardEvent('keyup',
    {
        keyCode: keyCode,
        which: keyCode,
        code: key,
        key: key,
        bubbles: true
    })
    el.dispatchEvent(evtPress)
}
//__________________________________________________________________________________

/*
───────────────────────────────────────────────────────────────────────────────────────────────────
─██████████████─██████████████─██████──────────██████─██████──██████─██████████████─██████████████─
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██████████──██░░██─██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██████████─██░░██████░░██─██░░░░░░░░░░██──██░░██─██░░██──██░░██─██░░██████░░██─██░░██████████─
─██░░██─────────██░░██──██░░██─██░░██████░░██──██░░██─██░░██──██░░██─██░░██──██░░██─██░░██─────────
─██░░██─────────██░░██████░░██─██░░██──██░░██──██░░██─██░░██──██░░██─██░░██████░░██─██░░██████████─
─██░░██─────────██░░░░░░░░░░██─██░░██──██░░██──██░░██─██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██─────────██░░██████░░██─██░░██──██░░██──██░░██─██░░██──██░░██─██░░██████░░██─██████████░░██─
─██░░██─────────██░░██──██░░██─██░░██──██░░██████░░██─██░░░░██░░░░██─██░░██──██░░██─────────██░░██─
─██░░██████████─██░░██──██░░██─██░░██──██░░░░░░░░░░██─████░░░░░░████─██░░██──██░░██─██████████░░██─
─██░░░░░░░░░░██─██░░██──██░░██─██░░██──██████████░░██───████░░████───██░░██──██░░██─██░░░░░░░░░░██─
─██████████████─██████──██████─██████──────────██████─────██████─────██████──██████─██████████████─
───────────────────────────────────────────────────────────────────────────────────────────────────
*/
//_________________________________________________________________
//var canvas_solid2 = document.getElementById('myCanvas_solid2');
/*var canvas_movable2 = document.getElementById('myCanvas_movable2')
var canvas_destroyable2 = document.getElementById('myCanvas_destroyable2')
var canvas_dangerous2 = document.getElementById('myCanvas_dangerous2')
var canvas_gettable2 = document.getElementById('myCanvas_gettable2')
var canvas_portal2 = document.getElementById('myCanvas_portal2')
var canvas_usable2 = document.getElementById('myCanvas_usable2')
var canvas_changeable2 = document.getElementById('myCanvas_changeable2')
var canvas_ui2 = document.getElementById('myCanvas_ui2')
var canvas_list2 = [canvas_solid2, canvas_movable2, canvas_destroyable2, canvas_dangerous2, canvas_gettable2, canvas_portal2, canvas_usable2, canvas_changeable2, canvas_ui2];
*/
var canvas_for_drawing = document.getElementById('myCanvas_drawing');


var canvas_solid = document.getElementById('myCanvas_solid');//set the URL from json later
var canvas_movable = document.getElementById('myCanvas_movable')
var canvas_destroyable = document.getElementById('myCanvas_destroyable')
var canvas_dangerous = document.getElementById('myCanvas_dangerous')
var canvas_gettable = document.getElementById('myCanvas_gettable')
var canvas_portal = document.getElementById('myCanvas_portal')
var canvas_usable = document.getElementById('myCanvas_usable')
var canvas_changeable = document.getElementById('myCanvas_changeable')
var canvas_ui = document.getElementById('myCanvas_ui')
var canvas_permeable = document.getElementById('myCanvas_permeable')
var canvas_list = [canvas_solid, canvas_movable, canvas_destroyable, canvas_dangerous, canvas_gettable, canvas_portal, canvas_usable, canvas_changeable, canvas_ui, canvas_permeable];
//_________________________________________________________________
/*
──────────────────────────────────────────────────────────────────────────────
─██████████████─██████──██████─██████████████─██████████████─██████──████████─
─██░░░░░░░░░░██─██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██░░░░██─
─██░░██████████─██░░██──██░░██─██░░██████████─██░░██████████─██░░██──██░░████─
─██░░██─────────██░░██──██░░██─██░░██─────────██░░██─────────██░░██──██░░██───
─██░░██─────────██░░██████░░██─██░░██████████─██░░██─────────██░░██████░░██───
─██░░██─────────██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██─────────██░░░░░░░░░░██───
─██░░██─────────██░░██████░░██─██░░██████████─██░░██─────────██░░██████░░██───
─██░░██─────────██░░██──██░░██─██░░██─────────██░░██─────────██░░██──██░░██───
─██░░██████████─██░░██──██░░██─██░░██████████─██░░██████████─██░░██──██░░████─
─██░░░░░░░░░░██─██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██░░░░██─
─██████████████─██████──██████─██████████████─██████████████─██████──████████─
──────────────────────────────────────────────────────────────────────────────
──────────────────────────────────────────────────────────────────────────────────
─██████████████───██████████████─████████──████████─██████████████─██████████████─
─██░░░░░░░░░░██───██░░░░░░░░░░██─██░░░░██──██░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██████░░██───██░░██████░░██─████░░██──██░░████─██░░██████████─██░░██████████─
─██░░██──██░░██───██░░██──██░░██───██░░░░██░░░░██───██░░██─────────██░░██─────────
─██░░██████░░████─██░░██──██░░██───████░░░░░░████───██░░██████████─██░░██████████─
─██░░░░░░░░░░░░██─██░░██──██░░██─────██░░░░░░██─────██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░████████░░██─██░░██──██░░██───████░░░░░░████───██░░██████████─██████████░░██─
─██░░██────██░░██─██░░██──██░░██───██░░░░██░░░░██───██░░██─────────────────██░░██─
─██░░████████░░██─██░░██████░░██─████░░██──██░░████─██░░██████████─██████████░░██─
─██░░░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░██──██░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─████████████████─██████████████─████████──████████─██████████████─██████████████─
──────────────────────────────────────────────────────────────────────────────────

*/

//__________________________________________________________________________________checkboxes
/*
var checkQ = document.getElementById("cbQ");
checkQ.addEventListener('change', function(e)
{
    checkQ.checked = !checkQ.checked
    simulate(checkQ, 81, "Q");
});

var checkW = document.getElementById("cbW");
checkW.addEventListener('change', function(e)
{
    checkW.checked = !checkW.checked
    simulate(checkW, 87, "W");
});
var checkE = document.getElementById("cbE");
checkE.addEventListener('change', function(e)
{
    checkE.checked = !checkE.checked
    simulate(checkE, 69, "E");
});
var checkA = document.getElementById("cbA");
checkA.addEventListener('change', function(e)
{
    checkA.checked = !checkA.checked
    simulate(checkA, 65, "A");
});
var checkS = document.getElementById("cbS");
checkS.addEventListener('change', function(e)
{
    checkS.checked = !checkS.checked
    simulate(checkS, 83, "S");
});
var checkD = document.getElementById("cbD");
checkD.addEventListener('change', function(e)
{
    checkD.checked = !checkD.checked
    simulate(checkD, 68, "D");
});
var checkZ = document.getElementById("cbZ");
checkZ.addEventListener('change', function(e)
{
    checkZ.checked = !checkZ.checked
    simulate(checkZ, 90, "Z");
});
var checkX = document.getElementById("cbX");
checkX.addEventListener('change', function(e)
{
    checkX.checked = !checkX.checked
    simulate(checkX, 88, "X");
});
var checkC = document.getElementById("cbC");
checkC.addEventListener('change', function(e)
{
    checkC.checked = !checkC.checked
    simulate(checkC, 67, "C");
});
var checkF = document.getElementById("cbF");
checkF.addEventListener('change', function(e)
{
    checkF.checked = !checkF.checked
    simulate(checkF, 70, "F");
});
*/
//_____________________________________________________________________________________
/*
─────────────────────────────────────────────────────────────────────
─────────██████─██████████████─██████████████─██████──────────██████─
─────────██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██████████──██░░██─
─────────██░░██─██░░██████████─██░░██████░░██─██░░░░░░░░░░██──██░░██─
─────────██░░██─██░░██─────────██░░██──██░░██─██░░██████░░██──██░░██─
─────────██░░██─██░░██████████─██░░██──██░░██─██░░██──██░░██──██░░██─
─────────██░░██─██░░░░░░░░░░██─██░░██──██░░██─██░░██──██░░██──██░░██─
─██████──██░░██─██████████░░██─██░░██──██░░██─██░░██──██░░██──██░░██─
─██░░██──██░░██─────────██░░██─██░░██──██░░██─██░░██──██░░██████░░██─
─██░░██████░░██─██████████░░██─██░░██████░░██─██░░██──██░░░░░░░░░░██─
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██████████░░██─
─██████████████─██████████████─██████████████─██████──────────██████─
─────────────────────────────────────────────────────────────────────

*/
//_____________________________________________________________________________________
var mydata = {};
var num = 0;
var output; //
var out_textures = {};
//_________________________________________

var i;//replace its name
/*
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
─██████████████───██████──██████─██████████████─██████████████─██████████████─██████──────────██████─██████████████─
─██░░░░░░░░░░██───██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██████████──██░░██─██░░░░░░░░░░██─
─██░░██████░░██───██░░██──██░░██─██████░░██████─██████░░██████─██░░██████░░██─██░░░░░░░░░░██──██░░██─██░░██████████─
─██░░██──██░░██───██░░██──██░░██─────██░░██─────────██░░██─────██░░██──██░░██─██░░██████░░██──██░░██─██░░██─────────
─██░░██████░░████─██░░██──██░░██─────██░░██─────────██░░██─────██░░██──██░░██─██░░██──██░░██──██░░██─██░░██████████─
─██░░░░░░░░░░░░██─██░░██──██░░██─────██░░██─────────██░░██─────██░░██──██░░██─██░░██──██░░██──██░░██─██░░░░░░░░░░██─
─██░░████████░░██─██░░██──██░░██─────██░░██─────────██░░██─────██░░██──██░░██─██░░██──██░░██──██░░██─██████████░░██─
─██░░██────██░░██─██░░██──██░░██─────██░░██─────────██░░██─────██░░██──██░░██─██░░██──██░░██████░░██─────────██░░██─
─██░░████████░░██─██░░██████░░██─────██░░██─────────██░░██─────██░░██████░░██─██░░██──██░░░░░░░░░░██─██████████░░██─
─██░░░░░░░░░░░░██─██░░░░░░░░░░██─────██░░██─────────██░░██─────██░░░░░░░░░░██─██░░██──██████████░░██─██░░░░░░░░░░██─
─████████████████─██████████████─────██████─────────██████─────██████████████─██████──────────██████─██████████████─
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

*/

//__________________________________________________________________________________
/*
$(document).on('click', '#bQ', function() {
    //var canvas = document.getElementsByTagName('canvas')[1];
    //var ctx = canvas.getContext("2d");
    //ctx.clearRect(0, 0, canvas.width, canvas.height);
    canvas_solid.width = 400;
    canvas_solid.height = 300;
  });*/

//var name_big = document.getElementById("name_big");


/*
var drawinn = document.getElementById("drawing_container");
var canvas_drawinn = document.getElementById("myCanvas_drawing");
draw_b(0, 0, canvas_drawinn, 808, 712);
drawinn.style.display = "none";



var bClose = document.getElementById("bClose");
bClose.onclick = function()
{
    is_big = 0;
    sizex = 4;
    sizey = 4;
    drawinn.style.display = "none";
    draw_picture(canvas_drawinn.toDataURL(), canvas_list[canvas_drawinn.affordance_id], 256, 224);
    canvas_drawinn.affordance_id = "-1";
    saveAffordanceImages();
};

var is_big = 0;

function enlarge_aff()
{
    is_big = 1;
    saveAffordanceImages();
    document.getElementById("name_big").textContent="Current affordance is: " + this.getAttribute("name");
    sizex = 12;
    sizey = 12;
    drawinn.style.display = "block";
    draw_picture(output["tag_images"][Object.keys(output["tag_images"])[this.getAttribute("affordance_id")]], canvas_drawinn, 768, 672);
    canvas_drawinn.affordance_id = this.getAttribute("affordance_id")
}

var bQ = document.getElementById("bQ");
bQ.onclick = enlarge_aff;
var bW = document.getElementById("bW");
bW.onclick = enlarge_aff;
var bE = document.getElementById("bE");
bE.onclick = enlarge_aff;
var bA = document.getElementById("bA");
bA.onclick = enlarge_aff;
var bS = document.getElementById("bS");
bS.onclick = enlarge_aff;
var bD = document.getElementById("bD");
bD.onclick = enlarge_aff;
var bZ = document.getElementById("bZ");
bZ.onclick = enlarge_aff;
var bX = document.getElementById("bX");
bX.onclick = enlarge_aff;
var bC = document.getElementById("bC");
bC.onclick = enlarge_aff;
var bF = document.getElementById("bF");
bF.onclick = enlarge_aff;
*/

function instructions()
{
    document.getElementById("myInstructions").style.width = "100%";
}

var button_reset = document.getElementById("button_reset");
button_reset.onclick = function()
{
    simulate(button_reset, 27, "ESC");
};



var button_done = document.getElementById("button_done");
button_done.onclick = function()
{
    simulate(button_done, 32, "Space");
    alert("Saved!");
};

const multi_button  = document.querySelector('.multi-button');
const btns = document.querySelectorAll('.btn'); 

multi_button.addEventListener('click', e => {

 btns.forEach(btn => {

    if(btn.getAttribute('id') === e.target.getAttribute('id'))
      btn.classList.add('active');
    else
      btn.classList.remove('active');
    });
});


const multi_button3  = document.querySelector('.multi-button3');
const btns1 = document.querySelectorAll('.btn1'); 

multi_button3.addEventListener('click', e => {

 btns1.forEach(btn1 => {

    if(btn1.getAttribute('id') === e.target.getAttribute('id'))
      btn1.classList.add('active');
      console.log("test");
    });
});
var button_square = document.getElementById("button_square");
button_square.onclick = function()
{
    isrect = 1;
};

var button_draw = document.getElementById("button_draw");
button_draw.onclick = function()
{
    isrect = 0;
};

function comment() 
{
    var cmt = prompt("Please enter your comment here", "");
    if (cmt != null) 
    {
      //save here
      alert("Saved");
    }
}

function closeInstr() 
{
  document.getElementById("myInstructions").style.width = "0";
}


function openNav() 
{
  document.getElementById("mySidenav").style.width = "250px";
}

function closeNav() 
{
  document.getElementById("mySidenav").style.width = "0";
}


var check_grid_on = 0;
// var button_grid = document.getElementById("button_grid");
// button_grid.style.backgroundColor = "gray";
// button_grid.style.fontSize = "x-large";
// button_grid.style.fontVariant = "small-caps";
// button_grid.onclick = function()
// {
//     if(!check_grid_on)
//     {
//         // for (var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
//         // {
//         //     drawGrid(canvas_list[canvas_id], 256, 224, GRID_SIZE, 'rgb(150, 150, 150)');
//         // }
//         drawGrid(canvas_draw, 256, 224, GRID_SIZE, 'rgb(250, 25, 25)')
//         check_grid_on = 1;
//     }
// };

// var button_grid_save = document.getElementById("button_grid_save");
// button_grid_save.style.backgroundColor = "darkgreen";
// button_grid_save.style.fontSize = "x-large";
// button_grid_save.style.fontVariant = "small-caps";
// button_grid_save.onclick = function()
// {
//     grid_checked = 1;
// };

// var button_grid_reset = document.getElementById("button_grid_reset");
// button_grid_reset.style.backgroundColor = "darkred";
// button_grid_reset.style.fontSize = "x-large";
// button_grid_reset.style.fontVariant = "small-caps";
// button_grid_reset.onclick = function()
// {
//     check_grid_on = 0;
//     grid_movex = 0;
//     grid_movey = 0;
//     for (var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
//     {
//         //erase(canvas_list[canvas_id]);
//         draw_b(0, 0, canvas_list[canvas_id], 256, 224);
//     }
// };
//
// var button_grid_up = document.getElementById("button_grid_up");
// button_grid_up.style.backgroundColor = 'rgb(100, 100, 100)';
// button_grid_up.style.fontSize = "x-large";
// button_grid_up.style.fontVariant = "small-caps";
// button_grid_up.onclick = function()
// {
//     grid_movey--;
//     for (var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
//     {
//         erase(canvas_list[canvas_id]);
//         draw_b(0, 0, canvas_list[canvas_id], 256, 224);
//         drawGrid(canvas_list[canvas_id], 256, 224, GRID_SIZE);
//     }
//
// };
//
// var button_grid_down = document.getElementById("button_grid_down");
// button_grid_down.style.backgroundColor = "gray";
// button_grid_down.style.fontSize = "x-large";
// button_grid_down.style.fontVariant = "small-caps";
// button_grid_down.onclick = function()
// {
//     grid_movey++;
//     for (var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
//     {
//         erase(canvas_list[canvas_id]);
//         draw_b(0, 0, canvas_list[canvas_id], 256, 224);
//         drawGrid(canvas_list[canvas_id], 256, 224, GRID_SIZE);
//     }
//
// };
//
// var button_grid_left = document.getElementById("button_grid_left");
// button_grid_left.style.backgroundColor = "gray";
// button_grid_left.style.fontSize = "x-large";
// button_grid_left.style.fontVariant = "small-caps";
// button_grid_left.onclick = function()
// {
//     grid_movex--;
//     for (var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
//     {
//         erase(canvas_list[canvas_id]);
//         draw_b(0, 0, canvas_list[canvas_id], 256, 224);
//         drawGrid(canvas_list[canvas_id], 256, 224, GRID_SIZE);
//     }
//
// };
//
// var button_grid_right = document.getElementById("button_grid_right");
// button_grid_right.style.backgroundColor = "gray";
// button_grid_right.style.fontSize = "x-large";
// button_grid_right.style.fontVariant = "small-caps";
// button_grid_right.onclick = function()
// {
//     grid_movex++;
//     for (var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
//     {
//         erase(canvas_list[canvas_id]);
//         draw_b(0, 0, canvas_list[canvas_id], 256, 224);
//         drawGrid(canvas_list[canvas_id], 256, 224, GRID_SIZE);
//     }
//
// };


function myFunction()
{
    var popup = document.getElementById("myPopup");
    popup.classList.toggle("show");
}


//__________________________________________________________________________________

/*
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
─████████████───████████████████───██████████████─██████──────────██████─██████████─██████──────────██████─██████████████─
─██░░░░░░░░████─██░░░░░░░░░░░░██───██░░░░░░░░░░██─██░░██──────────██░░██─██░░░░░░██─██░░██████████──██░░██─██░░░░░░░░░░██─
─██░░████░░░░██─██░░████████░░██───██░░██████░░██─██░░██──────────██░░██─████░░████─██░░░░░░░░░░██──██░░██─██░░██████████─
─██░░██──██░░██─██░░██────██░░██───██░░██──██░░██─██░░██──────────██░░██───██░░██───██░░██████░░██──██░░██─██░░██─────────
─██░░██──██░░██─██░░████████░░██───██░░██████░░██─██░░██──██████──██░░██───██░░██───██░░██──██░░██──██░░██─██░░██─────────
─██░░██──██░░██─██░░░░░░░░░░░░██───██░░░░░░░░░░██─██░░██──██░░██──██░░██───██░░██───██░░██──██░░██──██░░██─██░░██──██████─
─██░░██──██░░██─██░░██████░░████───██░░██████░░██─██░░██──██░░██──██░░██───██░░██───██░░██──██░░██──██░░██─██░░██──██░░██─
─██░░██──██░░██─██░░██──██░░██─────██░░██──██░░██─██░░██████░░██████░░██───██░░██───██░░██──██░░██████░░██─██░░██──██░░██─
─██░░████░░░░██─██░░██──██░░██████─██░░██──██░░██─██░░░░░░░░░░░░░░░░░░██─████░░████─██░░██──██░░░░░░░░░░██─██░░██████░░██─
─██░░░░░░░░████─██░░██──██░░░░░░██─██░░██──██░░██─██░░██████░░██████░░██─██░░░░░░██─██░░██──██████████░░██─██░░░░░░░░░░██─
─████████████───██████──██████████─██████──██████─██████──██████──██████─██████████─██████──────────██████─██████████████─
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
─────────────────────────────────────────────────────────────────────
─██████████████─██████████████─██████──────────██████─██████████████─
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██████████──██░░██─██░░░░░░░░░░██─
─██░░██████████─██░░██████████─██░░░░░░░░░░██──██░░██─██░░██████████─
─██░░██─────────██░░██─────────██░░██████░░██──██░░██─██░░██─────────
─██░░██████████─██░░██─────────██░░██──██░░██──██░░██─██░░██████████─
─██░░░░░░░░░░██─██░░██─────────██░░██──██░░██──██░░██─██░░░░░░░░░░██─
─██░░██████████─██░░██─────────██░░██──██░░██──██░░██─██████████░░██─
─██░░██─────────██░░██─────────██░░██──██░░██████░░██─────────██░░██─
─██░░██─────────██░░██████████─██░░██──██░░░░░░░░░░██─██████████░░██─
─██░░██─────────██░░░░░░░░░░██─██░░██──██████████░░██─██░░░░░░░░░░██─
─██████─────────██████████████─██████──────────██████─██████████████─
─────────────────────────────────────────────────────────────────────
*/
//_______________________________________________________________ different drawing fcns

function draw(x, y, z)
{

    if (z.getContext)
    {
        var ctx = z.getContext('2d');
        //drawing code here
        ctx.lineWidth = 3;
        ctx.fillStyle = "rgb(255, 255, 255)";
        ctx.fillRect (x, y, GRID_SIZE, GRID_SIZE);

        if (z == canvas_draw)
        {
            ctx.strokeStyle = 'rgb(255,0,  255)';
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, GRID_SIZE, GRID_SIZE)
        }
    }
    else
    {
        // canvas-unsupported code here
    }
}
function draw_b(x, y, z)
{

    if (z.getContext)
    {
        var ctx = z.getContext('2d');
        var width = z.width;
        var height = z.height;
        //drawing code here
        ctx.lineWidth = 3;
        ctx.fillStyle = "rgb(0, 0, 0, 0.7)";
        ctx.fillRect (x, y, width, height);
    }
    else
    {
        // canvas-unsupported code here
    }
}

function erase(x)
{
    if (x.getContext)
    {
        var ctx = x.getContext('2d');
        ctx.clearRect(0, 0, 256, 224)
    }
    else
    {
        // canvas-unsupported code here
    }
}

function draw_picture(x, z, size_x, size_y)
{
    if (z.getContext)
    {
        var ctx = z.getContext('2d');
        var img = new Image();
        //load image first ==v
        img.onload = function()
        {
            ctx.drawImage(img, 0, 0, size_x, size_y);
        };
        img.src = x;
    }
    else
    {
        console.log("canvas not found");
    }
}

draw_b(0, 0, canvas_for_drawing); //draw black on top of canvas

//__________________________________________________________________________________
/*
─────────────────────────────────────────────────────────────
─██████████████─████████████████───██████████─████████████───
─██░░░░░░░░░░██─██░░░░░░░░░░░░██───██░░░░░░██─██░░░░░░░░████─
─██░░██████████─██░░████████░░██───████░░████─██░░████░░░░██─
─██░░██─────────██░░██────██░░██─────██░░██───██░░██──██░░██─
─██░░██─────────██░░████████░░██─────██░░██───██░░██──██░░██─
─██░░██──██████─██░░░░░░░░░░░░██─────██░░██───██░░██──██░░██─
─██░░██──██░░██─██░░██████░░████─────██░░██───██░░██──██░░██─
─██░░██──██░░██─██░░██──██░░██───────██░░██───██░░██──██░░██─
─██░░██████░░██─██░░██──██░░██████─████░░████─██░░████░░░░██─
─██░░░░░░░░░░██─██░░██──██░░░░░░██─██░░░░░░██─██░░░░░░░░████─
─██████████████─██████──██████████─██████████─████████████───
─────────────────────────────────────────────────────────────

*/
/*var drawGrid = function(w, h, id) {
    var canvas = document.getElementById(id);
    var ctx = canvas.getContext('2d');
    ctx.canvas.width  = w;
    ctx.canvas.height = h;

    var data = '<svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg"> \
        <defs> \
            <pattern id="smallGrid" width="4" height="4" patternUnits="userSpaceOnUse"> \
                <path d="M 8 0 L 0 0 0 8" fill="none" stroke="gray" stroke-width="0.5" /> \
            </pattern> \
            <pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse"> \
                <rect width="80" height="80" fill="url(#smallGrid)" /> \
                <path d="M 80 0 L 0 0 0 80" fill="none" stroke="gray" stroke-width="1" /> \
            </pattern> \
        </defs> \
        <rect width="100%" height="100%" fill="url(#smallGrid)" /> \
    </svg>';

    var DOMURL = window.URL || window.webkitURL || window;

    var img = new Image();
    var svg = new Blob([data], {type: 'image/svg+xml;charset=utf-8'});
    var url = DOMURL.createObjectURL(svg);

    img.onload = function () {
      ctx.drawImage(img, 0, 0);
      DOMURL.revokeObjectURL(url);
    }
    img.src = url;
}*/

/*drawGrid(256, 224, "myCanvas_solid");
drawGrid(256, 224, "myCanvas_movable");
drawGrid(256, 224, "myCanvas_destroyable");
drawGrid(256, 224, "myCanvas_dangerous");
drawGrid(256, 224, "myCanvas_gettable");
drawGrid(256, 224, "myCanvas_portal");
drawGrid(256, 224, "myCanvas_usable");
drawGrid(256, 224, "myCanvas_changeable");
drawGrid(256, 224, "myCanvas_ui");*/


var grid_movex = 0;
var grid_movey = 0;
var grid_checked = 0;


var drawGrid = function(canvas, w, h, step, grid_color)
{
    var ctx = canvas.getContext('2d');
    ctx.beginPath();
    for (var x = -65536 + grid_movex; x <= w; x += step)
    {
            ctx.moveTo(x, 0);
            ctx.lineTo(x, h);
    }
    // set the color of the line
    ctx.strokeStyle = grid_color;
    ctx.lineWidth = 1;
    ctx.globalCompositeOperation='destination-out';
    ctx.globalCompositeOperation='source-over';
    // the stroke will actually paint the current path
    ctx.stroke();
    // for the sake of the example 2nd path
    ctx.beginPath();
    for (var y = -65536 + grid_movey; y <= h; y += step)
    {
            ctx.moveTo(0, y);
            ctx.lineTo(w, y);
    }
    // for your original question - you need to stroke only once
    ctx.stroke();
};
for (var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
{
    //drawGrid(canvas_list[canvas_id], 256, 224, GRID_SIZE);
}

//drawGrid(canvas_solid2, 256, 224, GRID_SIZE);

//__________________________________________________________________________________
/*
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
─████████████───████████████████───██████████████─██████──────────██████──────────██████████████─██████──────────██████─
─██░░░░░░░░████─██░░░░░░░░░░░░██───██░░░░░░░░░░██─██░░██──────────██░░██──────────██░░░░░░░░░░██─██░░██████████──██░░██─
─██░░████░░░░██─██░░████████░░██───██░░██████░░██─██░░██──────────██░░██──────────██░░██████░░██─██░░░░░░░░░░██──██░░██─
─██░░██──██░░██─██░░██────██░░██───██░░██──██░░██─██░░██──────────██░░██──────────██░░██──██░░██─██░░██████░░██──██░░██─
─██░░██──██░░██─██░░████████░░██───██░░██████░░██─██░░██──██████──██░░██──────────██░░██──██░░██─██░░██──██░░██──██░░██─
─██░░██──██░░██─██░░░░░░░░░░░░██───██░░░░░░░░░░██─██░░██──██░░██──██░░██──────────██░░██──██░░██─██░░██──██░░██──██░░██─
─██░░██──██░░██─██░░██████░░████───██░░██████░░██─██░░██──██░░██──██░░██──────────██░░██──██░░██─██░░██──██░░██──██░░██─
─██░░██──██░░██─██░░██──██░░██─────██░░██──██░░██─██░░██████░░██████░░██──────────██░░██──██░░██─██░░██──██░░██████░░██─
─██░░████░░░░██─██░░██──██░░██████─██░░██──██░░██─██░░░░░░░░░░░░░░░░░░██──────────██░░██████░░██─██░░██──██░░░░░░░░░░██─
─██░░░░░░░░████─██░░██──██░░░░░░██─██░░██──██░░██─██░░██████░░██████░░██──────────██░░░░░░░░░░██─██░░██──██████████░░██─
─████████████───██████──██████████─██████──██████─██████──██████──██████──────────██████████████─██████──────────██████─
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
───────────────────────────────────────────────────────────────────────────────────────────────────────
─██████████████─██████████████─████████████████───██████████████─██████████████─██████──────────██████─
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░░░██───██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██████████──██░░██─
─██░░██████████─██░░██████████─██░░████████░░██───██░░██████████─██░░██████████─██░░░░░░░░░░██──██░░██─
─██░░██─────────██░░██─────────██░░██────██░░██───██░░██─────────██░░██─────────██░░██████░░██──██░░██─
─██░░██████████─██░░██─────────██░░████████░░██───██░░██████████─██░░██████████─██░░██──██░░██──██░░██─
─██░░░░░░░░░░██─██░░██─────────██░░░░░░░░░░░░██───██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██░░██──██░░██─
─██████████░░██─██░░██─────────██░░██████░░████───██░░██████████─██░░██████████─██░░██──██░░██──██░░██─
─────────██░░██─██░░██─────────██░░██──██░░██─────██░░██─────────██░░██─────────██░░██──██░░██████░░██─
─██████████░░██─██░░██████████─██░░██──██░░██████─██░░██████████─██░░██████████─██░░██──██░░░░░░░░░░██─
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██████████░░██─
─██████████████─██████████████─██████──██████████─██████████████─██████████████─██████──────────██████─
───────────────────────────────────────────────────────────────────────────────────────────────────────
*/

//__________________________________________________________________________________good drawing code

var shift_down = 0;
var mouseDown = 0;
var sizex = 4;
var sizey = 2;
var firstlog = 1;
var rect_x1 = 0;
var rect_y1 = 0;
var rect_x2 = 0;
var rect_y2 = 0;
var isrect = 0;




function draw_mouse_affordances(tmp, canvas, e)
{
    var context = canvas.getContext("2d");
    var pos = getMousePos(canvas, e);
    //var canvas_check = document.elementFromPoint(pos.x, pos.y);

    if(mouseDown)
    {   
        if (isrect)
        {
            if (firstlog == 1)
            {

                console.log(pos);
                rect_x1 = pos.x;
                rect_y1 = pos.y;
                firstlog = 0;
            }
        }
        context.fillStyle = color;
    	context.fillRect(pos.x - ((pos.x /*- grid_movex*/) % sizex), pos.y - ((pos.y /*- grid_movey*/) % sizey), sizex, sizey);
    }
    if (!mouseDown)
    {
        if (isrect)
        {
            if (firstlog == 0)
            {
                console.log(pos);
                rect_x2 = pos.x;
                rect_y2 = pos.y;
                firstlog = 1;
                context.fillStyle = "white";
                context.fillRect(rect_x1, rect_y1, ((rect_x2-rect_x1)+4), (rect_y2-rect_y1));
            }
        }
    }
}

for (var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
{
    canvas_for_drawing.onmousedown = function()
    {
        event.preventDefault();
        if(event.button == 0)
        {
            ++mouseDown;
            if (isrect)
            {
                color = "rgba(255, 255, 255, 0)";
            }
            else
            {
                color = "white";
            }        
        }
        if(event.button == 2)
        {
            if (!isrect)
            {
                ++mouseDown;
                color = "black";
            }
            
        }
    }
    canvas_for_drawing.onmouseup = function()
    {
        event.preventDefault();
        if(event.button == 0)
        {

            --mouseDown;
            if (isrect)
            {
                color = "rgba(255, 255, 255, 0)";
            }
            
        }
        if(event.button == 2)
        {

            --mouseDown;
            color = "black";
        }
    }
    window.addEventListener('mousemove', draw_mouse_affordances.bind(null, event, canvas_for_drawing), false);
    window.addEventListener('mousedown', draw_mouse_affordances.bind(null, event, canvas_for_drawing), false);
    canvas_for_drawing.addEventListener('contextmenu', event => event.preventDefault());//block rightclick on 'em
}
//----------------------------------------------------------------------------

//----------------------------------------------------------------------------

function getMousePos(canvas, evt)
{
    var rect = canvas.getBoundingClientRect();
    return {
        x: (evt.clientX - rect.left) / (rect.right - rect.left) * canvas.width,
        y: (evt.clientY - rect.top) / (rect.bottom - rect.top) * canvas.height
    };
};

//-------------------------------------------------------------------------------------------------------------------------------------------------------

/*var canvas = new fabric.Canvas('myCanvas_drawing', { selection: false });

var rect, isDown, origX, origY;

canvas.on('mouse:down', function(o){
    isDown = true;
    var pointer = canvas.getPointer(o.e);
    origX = pointer.x;
    origY = pointer.y;
    var pointer = canvas.getPointer(o.e);
    rect = new fabric.Rect({
        left: origX,
        top: origY,
        originX: 'left',
        originY: 'top',
        width: pointer.x-origX,
        height: pointer.y-origY,
        angle: 0,
        fill: 'rgba(255,0,0,0.5)',
        transparentCorners: false
    });
    canvas.add(rect);
});

canvas.on('mouse:move', function(o){
    if (!isDown) return;
    var pointer = canvas.getPointer(o.e);
    
    if(origX>pointer.x){
        rect.set({ left: Math.abs(pointer.x) });
    }
    if(origY>pointer.y){
        rect.set({ top: Math.abs(pointer.y) });
    }
    
    rect.set({ width: Math.abs(origX - pointer.x) });
    rect.set({ height: Math.abs(origY - pointer.y) });
    
    
    canvas.renderAll();
});

canvas.on('mouse:up', function(o){
  isDown = false;
});
*/



//__________________________________________________________________________________
/*
────────────────────────────────────────────────────────────────
─██████─────────██████████████─██████████████─████████████──────
─██░░██─────────██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░████────
─██░░██─────────██░░██████░░██─██░░██████░░██─██░░████░░░░██────
─██░░██─────────██░░██──██░░██─██░░██──██░░██─██░░██──██░░██────
─██░░██─────────██░░██──██░░██─██░░██████░░██─██░░██──██░░██────
─██░░██─────────██░░██──██░░██─██░░░░░░░░░░██─██░░██──██░░██────
─██░░██─────────██░░██──██░░██─██░░██████░░██─██░░██──██░░██────
─██░░██─────────██░░██──██░░██─██░░██──██░░██─██░░██──██░░██────
─██░░██████████─██░░██████░░██─██░░██──██░░██─██░░████░░░░██────
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██░░██─██░░░░░░░░████────
─██████████████─██████████████─██████──██████─████████████──────
────────────────────────────────────────────────────────────────
─────────────────────────────────────────────────────────────
─██████████████─██████████████─██████████████─██████████████─
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██████░░██─██░░██████░░██─██░░██████████─██░░██████████─
─██░░██──██░░██─██░░██──██░░██─██░░██─────────██░░██─────────
─██░░██████░░██─██░░██████░░██─██░░██─────────██░░██████████─
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██████─██░░░░░░░░░░██─
─██░░██████████─██░░██████░░██─██░░██──██░░██─██░░██████████─
─██░░██─────────██░░██──██░░██─██░░██──██░░██─██░░██─────────
─██░░██─────────██░░██──██░░██─██░░██████░░██─██░░██████████─
─██░░██─────────██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██████─────────██████──██████─██████████████─██████████████─
─────────────────────────────────────────────────────────────

*/
//__________________________________________________________________________________load the stuff
var $ = window.jQuery;
window.addEventListener('load', function()
{
    console.log('on load')
    fetch_data();
})

function fetch_data(){
  console.log(mydata)
  temp_url = BASE_URL + "/expert/get_image?tagger=" + TAGGER_ID
  $.getJSON(temp_url, function(json)
  {
      mydata = json;
      console.log(mydata);
      console.log(mydata["output"]) // this will show the info it in firebug console
      output =
      {
          "tagger_id":TAGGER_ID,
          "image_id":mydata.output.image_id
      };
      console.log('output w/ tagger')
      console.log(output)
      for (var index = 0; index < Object.keys(mydata["output"]['textures']).length; index++)
      {
          var texture_index = 'texture_' + index;
          var act_texture = mydata.output.textures[texture_index];
          out_textures[texture_index] =
          {
              "texture_id": act_texture['texture_id'],
              "solid":0,
              "movable":0,
              "destroyable":0,
              "dangerous":0,
              "gettable":0,
              "portal":0,
              "usable":0,
              "changeable":0,
              "ui":0,
              "permeable":0,
          };
       }
       console.log(mydata)
       update_images()
  });
}

function update_images(){
    console.log(mydata["output"]['image'])
    console.log(mydata["output"]['solid'])
    var drawinn_img = document.getElementById('drawer');
    drawinn_img.src = mydata["output"]['image'];
    var solid_img = document.getElementById('solid');
    solid_img.src = mydata["output"]['image'];
    var solid_img = document.getElementById('solid');
    solid_img.src = mydata["output"]['image'];
    var mov_img = document.getElementById('movable');
    mov_img.src = mydata["output"]['image'];
    var dest_img = document.getElementById('destroyable');
    dest_img.src = mydata["output"]['image'];
    var dang_img = document.getElementById('dangerous');
    dang_img.src = mydata["output"]['image'];
    var get_img = document.getElementById('gettable');
    get_img.src = mydata["output"]['image'];
    var port_img = document.getElementById('portal');
    port_img.src = mydata["output"]['image'];
    var us_img = document.getElementById('usable');
    us_img.src = mydata["output"]['image'];
    var chang_img = document.getElementById('changeable');
    chang_img.src = mydata["output"]['image'];
    var ui_img = document.getElementById('ui');
    ui_img.src = mydata["output"]['image'];
    var permeable_img = document.getElementById('permeable');
    permeable_img.src = mydata["output"]['image'];
    var scrn_img = document.getElementById('screenshot_preview');
    scrn_img.src = mydata["output"]['image'];
    var texture_tmp = document.getElementById('texture');
    texture_tmp.src = mydata["output"]['textures']['texture_0']['texture_data'];

    document.getElementById("curr_textures").textContent=String(num) + "/" + String(Object.keys(mydata["output"]['textures']).length) + " textures";


    grid_movex = mydata["output"]['x_offset']
    grid_movey = mydata["output"]['y_offset']
    console.log(grid_movex)
    console.log(grid_movey)
    //drawGrid(canvas_draw, 256, 224, GRID_SIZE, 'rgb(250, 25, 25)')
    check_grid_on = 1;
    grid_checked = 1;

    var poses = mydata["output"]['textures']['texture_' + num]['locations'];
    for(i = 0; i < Object.keys(poses).length; i++)
    {
        pos_x = poses['location_' + i]['x'];
        pos_y = poses['location_' + i]['y'];
        draw(pos_x, pos_y, canvas_draw);
    }
    checkQ.checked = false;
    checkW.checked = false;
    checkE.checked = false;
    checkA.checked = false;
    checkS.checked = false;
    checkD.checked = false;
    checkZ.checked = false;
    checkX.checked = false;
    checkC.checked = false;
    checkF.checked = false;
}

function send_output_to_server(){
    console.log('Space pressed submitting')
    console.log(output)
    var tmp_url = BASE_URL + "/api/insert"
    $.ajax({
      url: tmp_url,
      type: "post",
      data: JSON.stringify(output),
      contentType: "application/json",
      success: function (data) {
        console.log('Sent labels to server /submit_tags')
        console.log(data)
      }
    });
}
//__________________________________________________________________________________
/*
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
─██████████████─██████─────────██████────────────██████──████████─██████████████─████████──████████─██████████████─
─██░░░░░░░░░░██─██░░██─────────██░░██────────────██░░██──██░░░░██─██░░░░░░░░░░██─██░░░░██──██░░░░██─██░░░░░░░░░░██─
─██░░██████░░██─██░░██─────────██░░██────────────██░░██──██░░████─██░░██████████─████░░██──██░░████─██░░██████████─
─██░░██──██░░██─██░░██─────────██░░██────────────██░░██──██░░██───██░░██───────────██░░░░██░░░░██───██░░██─────────
─██░░██████░░██─██░░██─────────██░░██────────────██░░██████░░██───██░░██████████───████░░░░░░████───██░░██████████─
─██░░░░░░░░░░██─██░░██─────────██░░██────────────██░░░░░░░░░░██───██░░░░░░░░░░██─────████░░████─────██░░░░░░░░░░██─
─██░░██████░░██─██░░██─────────██░░██────────────██░░██████░░██───██░░██████████───────██░░██───────██████████░░██─
─██░░██──██░░██─██░░██─────────██░░██────────────██░░██──██░░██───██░░██───────────────██░░██───────────────██░░██─
─██░░██──██░░██─██░░██████████─██░░██████████────██░░██──██░░████─██░░██████████───────██░░██───────██████████░░██─
─██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██────██░░██──██░░░░██─██░░░░░░░░░░██───────██░░██───────██░░░░░░░░░░██─
─██████──██████─██████████████─██████████████────██████──████████─██████████████───────██████───────██████████████─
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
────────────────────────────────────────────────────────────────────
─██████████████─██████████████─████████████████───██████████████────
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░░░██───██░░░░░░░░░░██────
─██░░██████████─██░░██████░░██─██░░████████░░██───██░░██████████────
─██░░██─────────██░░██──██░░██─██░░██────██░░██───██░░██────────────
─██░░██─────────██░░██──██░░██─██░░████████░░██───██░░██████████────
─██░░██─────────██░░██──██░░██─██░░░░░░░░░░░░██───██░░░░░░░░░░██────
─██░░██─────────██░░██──██░░██─██░░██████░░████───██░░██████████────
─██░░██─────────██░░██──██░░██─██░░██──██░░██─────██░░██────────────
─██░░██████████─██░░██████░░██─██░░██──██░░██████─██░░██████████────
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██░░░░░░██─██░░░░░░░░░░██────
─██████████████─██████████████─██████──██████████─██████████████────
────────────────────────────────────────────────────────────────────

*/
//__________________________________________________________________________________actual keys
/*document.onkeyup = function(event)
{
    switch (event.keyCode)
    {
        case GRID_SIZE: //do this if want shift
            shift_down = 0;
        break;
    }
}*/
function flip_affordance(whichcheckbox, whichcanvas){
    if(whichcheckbox.checked)
    {
        poses = mydata["output"]['textures']['texture_' + num]['locations'];
        for(i = 0; i < Object.keys(poses).length; i++)
        {
            pos_x = poses['location_' + i]['x'];
            pos_y = poses['location_' + i]['y'];
            draw_b(pos_x, pos_y, whichcanvas, GRID_SIZE, GRID_SIZE);
        }
        out_textures['texture_'+num]['solid'] = 0;
        whichcheckbox.checked = false;

    }
    else{
        poses = mydata["output"]['textures']['texture_' + num]['locations'];
        for(i = 0; i < Object.keys(poses).length; i++)
        {
            pos_x = poses['location_' + i]['x'];
            pos_y = poses['location_' + i]['y'];
            draw(pos_x, pos_y, whichcanvas);
        }
        out_textures['texture_'+num]['solid'] = 1;//do for all affordances!!!!!!!!!!!!!
        whichcheckbox.checked = true;
    }
}

function saveAffordanceImages(){
  output["tag_images"] =
  {
      "solid": canvas_solid.toDataURL(),
      "movable":canvas_movable.toDataURL(),
      "destroyable":canvas_destroyable.toDataURL(),
      "dangerous":canvas_dangerous.toDataURL(),
      "gettable":canvas_gettable.toDataURL(),
      "portal":canvas_portal.toDataURL(),
      "usable":canvas_usable.toDataURL(),
      "changeable":canvas_changeable.toDataURL(),
      "ui":canvas_ui.toDataURL(),
      "permeable":canvas_permeable.toDataURL(),
  }
  console.log('saved to output[tagimages]')
}

var CHECK_GRID = 0;
document.onkeydown = function(event)
{
    var pos_x = 0;
    var pos_y = 0;
    var textures = mydata["output"]['textures'];
    var poses = mydata["output"]['textures']['texture_' + num]['locations'];
    switch (event.keyCode)
    {
        case 8: //Backspace
                erase(canvas_draw);
                if(CHECK_GRID)
                {
                    for(var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
                    {
                        drawGrid(canvas_list[canvas_id], 256, 224, 16, 'rgb(0, 0, 0)');
                        drawGrid(canvas_list[canvas_id], 256, 224, 16, 'rgb(0, 0, 0)');
                        drawGrid(canvas_list[canvas_id], 256, 224, 16, 'rgb(150, 150, 150)');
                    }
                }

                num = num - 1;
                if (num == -1)//check evr time that num doesnt exceed amount of textures
                {
                    num = num + 1;
                    alert('Out of textures. Current texture num = ' + num);
                }

                texture.src = textures['texture_' + num]['texture_data'];
                poses = mydata["output"]['textures']['texture_' + num]['locations'];

                for(i = 0; i < Object.keys(poses).length; i++)
                {
                    pos_x = poses['location_' + i]['x'];
                    pos_y = poses['location_' + i]['y'];
                    draw(pos_x, pos_y, canvas_draw);
                }
                //checkboxes_____________________________________________________
                checkQ.checked = false;
                checkW.checked = false;
                checkE.checked = false;
                checkA.checked = false;
                checkS.checked = false;
                checkD.checked = false;
                checkZ.checked = false;
                checkX.checked = false;
                checkC.checked = false;
                checkF.checked = false;
                //
                saveAffordanceImages();
                document.getElementById("curr_textures").textContent=String(num) + "/" + String(Object.keys(mydata["output"]['textures']).length) + " textures";
        break;
        case 13: //ENTER
            if(grid_checked)
            {
                erase(canvas_draw);
                if(CHECK_GRID)
                {
                    for(var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
                    {
                        drawGrid(canvas_list[canvas_id], 256, 224, GRID_SIZE, 'rgb(0, 0, 0)');
                        drawGrid(canvas_list[canvas_id], 256, 224, GRID_SIZE, 'rgb(0, 0, 0)');
                        drawGrid(canvas_list[canvas_id], 256, 224, GRID_SIZE, 'rgb(150, 150, 150)');
                    }
                }

                num = num + 1;
                if (num == (Object.keys(textures).length))//check evr time that num doesnt exceed amount of textures
                {
                    num = num - 1;
                    alert('Out of textures. Last texture num = ' + num);
                }

                texture.src = textures['texture_' + num]['texture_data'];
                poses = mydata["output"]['textures']['texture_' + num]['locations'];
                //drawGrid(canvas_draw, 256, 224, GRID_SIZE, 'rgb(250, 25, 25)')
                for(i = 0; i < Object.keys(poses).length; i++)
                {
                    pos_x = poses['location_' + i]['x'];
                    pos_y = poses['location_' + i]['y'];
                    draw(pos_x, pos_y, canvas_draw);
                }

                //checkboxes_____________________________________________________
                checkQ.checked = false;
                checkW.checked = false;
                checkE.checked = false;
                checkA.checked = false;
                checkS.checked = false;
                checkD.checked = false;
                checkZ.checked = false;
                checkX.checked = false;
                checkC.checked = false;
                //
                saveAffordanceImages();
                document.getElementById("curr_textures").textContent=String(num) + "/" + String(Object.keys(mydata["output"]['textures']).length) + " textures";

            }
            else
            {
                alert("align the grid first!");
            }
            //__________________________________________________________
        break;
        case 32: //space to save
            saveAffordanceImages();
            output["textures"] = out_textures
            send_output_to_server();
        break;
        //____________________vvv keypress to draw on affordances squares vvv
        case 81: //q
            flip_affordance(checkQ, canvas_solid)
        break;

        case 87: //w
            flip_affordance(checkW, canvas_movable)
        break;

        case 69: //e
            flip_affordance(checkE, canvas_destroyable)
        break;
        case 65: //a
            flip_affordance(checkA, canvas_dangerous)
        break;
        case 83: //s
            flip_affordance(checkS, canvas_gettable)
        break;
        case 68: //d
            flip_affordance(checkD, canvas_portal)
        break;

        case 90: //z
            flip_affordance(checkZ, canvas_usable)
        break;

        case 88: //x
            flip_affordance(checkX, canvas_changeable)
        break;

        case 67: // c
            flip_affordance(checkC, canvas_ui)
        break;

        case 70: // f
            flip_affordance(checkF, canvas_permeable)
        break;

        case 27: // ECS
            //if(!is_big)
            //{
                draw_b(0, 0, myCanvas_drawing);
                /*
                poses = mydata["output"]['textures']['texture_' + num]['locations'];
                for(i = 0; i < Object.keys(poses).length; i++)
                {
                    pos_x = poses['location_' + i]['x'];
                    pos_y = poses['location_' + i]['y'];
                    
                    /*
                    draw_b(pos_x, pos_y, canvas_dangerous, GRID_SIZE, GRID_SIZE);
                    draw_b(pos_x, pos_y, canvas_movable, GRID_SIZE, GRID_SIZE);
                    draw_b(pos_x, pos_y, canvas_destroyable, GRID_SIZE, GRID_SIZE);
                    draw_b(pos_x, pos_y, canvas_ui, GRID_SIZE, GRID_SIZE);
                    draw_b(pos_x, pos_y, canvas_gettable, GRID_SIZE, GRID_SIZE);
                    draw_b(pos_x, pos_y, canvas_portal, GRID_SIZE, GRID_SIZE);
                    draw_b(pos_x, pos_y, canvas_usable, GRID_SIZE, GRID_SIZE);
                    draw_b(pos_x, pos_y, canvas_changeable, GRID_SIZE, GRID_SIZE);
                    draw_b(pos_x, pos_y, canvas_permeable, GRID_SIZE, GRID_SIZE);
                    
                    out_textures['texture_'+num]['solid'] = 0;
                    out_textures['texture_'+num]['movable'] = 0;
                    out_textures['texture_'+num]['destroyable'] = 0;
                    out_textures['texture_'+num]['dangerous'] = 0;
                    out_textures['texture_'+num]['gettable'] = 0;
                    out_textures['texture_'+num]['portal'] = 0;
                    out_textures['texture_'+num]['usable'] = 0;
                    out_textures['texture_'+num]['changeable'] = 0;
                    out_textures['texture_'+num]['ui'] = 0;
                    out_textures['texture_'+num]['permeable'] = 0;
                    
                    checkQ.checked = false;
                    checkW.checked = false;
                    checkE.checked = false;
                    checkA.checked = false;
                    checkS.checked = false;
                    checkD.checked = false;
                    checkZ.checked = false;
                    checkX.checked = false;
                    checkC.checked = false;
                    checkF.checked = false;
                    
                }
                //save and load current state of affordances here
                //var solid_img = document.getElementById('solid');
                if(num == 0)
                {
                    for (var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
                    {
                        draw_b(0, 0, canvas_list[canvas_id], 256, 224);
                    }
                }
                else
                {
                    for (var canvas_id = 0; canvas_id < canvas_list.length; canvas_id++)
                    {
                        draw_picture(output["tag_images"][Object.keys(output["tag_images"])[canvas_id]], canvas_list[canvas_id], 256, 224);
                    }
                }
            */
            //}
            //else
            //{
            //    alert("Close the big image first!");
            //}
        break;

        /*case GRID_SIZE: do this if want shift
            shift_down = 1;
        break;*/
    }
}
