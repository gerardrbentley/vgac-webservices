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
     ////console.log('staging site base url')
     BASE_URL = '/staging'
}
else{
     ////console.log('live site url')
}

// Gets the tagger id from query string param (in url anything after ? -> ?tagger=xyz)
const queryString = window.location.search
const urlParams = new URLSearchParams(queryString)
var TAGGER_ID = 'no-tagger'
if (urlParams.has('tagger')){
    TAGGER_ID = urlParams.get('tagger')
    ////console.log('tagger id got from url')
}
else {
    ////console.log('no tagger id in url')
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

var canvas_for_drawing = document.getElementById('myCanvas_drawing');
var canvas_for_drawing_square = document.getElementById('myCanvas_drawing_square');


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
var out_tmp = {};
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
function instructions()
{
    document.getElementById("myInstructions").style.width = "100%";
}

var button_reset = document.getElementById("button_reset");
button_reset.onclick = function()
{
    //simulate(button_reset, 1027, "ESC");
    
    if (end_of_tagging == false)
    {
        for (var i = 0; i < 10; i++)
        {
            cb_list[i].checked = false;
        }
        draw_b(0, 0, myCanvas_drawing);
        for (var i = 0; i < 10; i++)
        {
                var atb = cb_list[i].getAttribute("aff");
                out_textures["tile_" + num][atb] = 0;  
        }
        poses = mydata["output"]['tiles']['tile_' + num]['locations'];
        //console.log("poses");
        //console.log(poses);
        for(i = 0; i < Object.keys(poses).length; i++)
        {
            pos_x = poses['location_' + i]['x'];
            pos_x = alt_posx(pos_x, canvas_for_drawing);
            pos_y = poses['location_' + i]['y'];
            pos_y = alt_posy(pos_y, canvas_for_drawing);
            draw(pos_x, pos_y, canvas_for_drawing);
        }
        if(num == 0)
        {
            draw_b(0, 0, myCanvas_drawing, 2506, 2204);
        }
        console.log("erase_save")
        saveAffordanceImages();
    }
    else 
    {
        console.log("erase pressed");
        erase(canvas_for_drawing);
        draw_b(0, 0, canvas_for_drawing);
        
        for (var i = 0; i < cb_list.length; i++)
        {
            if(cb_list[i].checked == true)
            {
                console.log(cb_list[i]);
                console.log(out_tmp);
                console.log("output");
                console.log(output);
                var auf = cb_list[i].getAttribute("aff");
                console.log(auf);
                draw_picture(out_tmp["affordance_images"][auf], canvas_for_drawing, canvas_for_drawing.width, canvas_for_drawing.height);
            }
        }
        //saveAffordanceImages();
    }
};
var ALERT_TITLE = "Oops!";
var ALERT_BUTTON_TEXT = "Ok";

if(document.getElementById) {
	window.alert = function(txt) {
		createCustomAlert(txt);
	}
}

function createCustomAlert(txt) {
	d = document;

	if(d.getElementById("modalContainer")) return;

	mObj = d.getElementsByTagName("body")[0].appendChild(d.createElement("div"));
	mObj.id = "modalContainer";
	mObj.style.height = d.documentElement.scrollHeight + "px";
	
	alertObj = mObj.appendChild(d.createElement("div"));
	alertObj.id = "alertBox";
	if(d.all && !window.opera) alertObj.style.top = document.documentElement.scrollTop + "px";
	alertObj.style.left = (d.documentElement.scrollWidth - alertObj.offsetWidth)/2 + "px";
	alertObj.style.visiblity="visible";

	h1 = alertObj.appendChild(d.createElement("h1"));
	h1.appendChild(d.createTextNode(ALERT_TITLE));

	msg = alertObj.appendChild(d.createElement("p"));
	//msg.appendChild(d.createTextNode(txt));
	msg.innerHTML = txt;

	btn = alertObj.appendChild(d.createElement("a"));
	btn.id = "clseButn";
	btn.appendChild(d.createTextNode(ALERT_BUTTON_TEXT));
	btn.href = "#";
	btn.focus();
	btn.onclick = function() { removeCustomAlert();return false; }

	alertObj.style.display = "block";
	
}

function removeCustomAlert() {
	document.getElementsByTagName("body")[0].removeChild(document.getElementById("modalContainer"));
}
function ful(){
alert('Alert this pages');
}


var button_done = document.getElementById("button_done");
button_done.onclick = function()
{
    simulate(button_done, 1000, "Space");
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



var button_square = document.getElementById("button_square");
button_square.onclick = function()
{
    isrect = 1;
    isdraw = 0;
};

var button_draw = document.getElementById("button_draw");
button_draw.onclick = function()
{
    isrect = 0;
    isdraw = 1;
};

var button_next = document.getElementById("button_next");
button_next.onclick = function()
{
    simulate(button_next, 165, "ù");
};

var button_back = document.getElementById("button_back");
button_back.onclick = function()
{
    simulate(button_back, 162, "؛");
};
button_back.disabled = false;
button_next.disabled = false;
function comment() 
{
    var cmt = prompt("Please enter your comment here", "");
    if (cmt != null) 
    {
      //save here
      alert("Saved");
    }
}



var b_dang = document.getElementById("button_1");
b_dang.checked = false;
b_dang.onclick = function()
{
    ////console.log(document.getElementById("myCanvas_drawing1"));
    if (end_of_tagging == true)
    {
        goDraw(b_dang);
    }
    else
    {
        flip_affordance(b_dang, document.getElementById("myCanvas_drawing1"));
    }
};
var b_sol = document.getElementById("button_2");
b_sol.checked = false;
b_sol.onclick = function()
{
    if (end_of_tagging == true)
    {
        goDraw(b_sol);
    }
    else
    {
        flip_affordance(b_sol, document.getElementById("myCanvas_drawing2"));
    }
};
var b_perm = document.getElementById("button_3");
b_perm.checked = false;
b_perm.onclick = function()
{
    if (end_of_tagging == true)
    {
        goDraw(b_perm);
    }
    else
    {
        flip_affordance(b_perm, document.getElementById("myCanvas_drawing3"));
    }
};
var b_chng = document.getElementById("button_4");
b_chng.checked = false;
b_chng.onclick = function()
{
    if (end_of_tagging == true)
    {
        goDraw(b_chng);
    }
    else
    {
        flip_affordance(b_chng, document.getElementById("myCanvas_drawing4"));
    }
};
var b_move = document.getElementById("button_5");
b_move.checked = false;
b_move.onclick = function()
{
    if (end_of_tagging == true)
    {
        goDraw(b_move);
    }
    else
    {
        flip_affordance(b_move, document.getElementById("myCanvas_drawing5"));
    }
};
var b_dest = document.getElementById("button_6");
b_dest.checked = false;
b_dest.onclick = function()
{
    if (end_of_tagging == true)
    {
        goDraw(b_dest);
    }
    else
    {
        flip_affordance(b_dest, document.getElementById("myCanvas_drawing6"));
    }
};
var b_gett = document.getElementById("button_7");
b_gett.checked = false;
b_gett.onclick = function()
{
    if (end_of_tagging == true)
    {
        goDraw(b_gett);
    }
    else
    {
        flip_affordance(b_gett, document.getElementById("myCanvas_drawing7"));
    }
};
var b_usab = document.getElementById("button_8");
b_usab.checked = false;
b_usab.onclick = function()
{
    if (end_of_tagging == true)
    {
        goDraw(b_usab);
    }
    else
    {
        flip_affordance(b_usab, document.getElementById("myCanvas_drawing8"));
    }
};
var b_port = document.getElementById("button_9");
b_port.checked = false;
b_port.onclick = function()
{
    if (end_of_tagging == true)
    {
        goDraw(b_port);
    }
    else
    {
        flip_affordance(b_port, document.getElementById("myCanvas_drawing9"));
    }
};
var b_ui = document.getElementById("button_10");
b_ui.checked = false;
b_ui.onclick = function()
{
    if (end_of_tagging == true)
    {
        goDraw(b_ui);
    }
    else
    {
        flip_affordance(b_ui, document.getElementById("myCanvas_drawing10"));
    }
};
var cb_list = [b_dang, b_chng, b_dest, b_gett, b_move, b_perm, b_port, b_sol, b_ui, b_usab];

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
        ctx.fillRect (x, y, z.width/15.8, z.height/13.9);

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
function draw_b(x, y, canv)
{

    if (canv.getContext)
    {
        var ctx = canv.getContext('2d');
        var width = canv.width;
        var height = canv.height;
        //drawing code here
        ctx.lineWidth = 3;
        ctx.fillStyle = "rgb(0, 0, 0)";
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
        ctx.clearRect(0, 0, 1000, 1000)
    }
    else
    {
        // canvas-unsupported code here
    }
}

function draw_picture(source, canv, size_x, size_y)
{
    if (canv.getContext)
    {
        var ctx = canv.getContext('2d');
        var img = new Image();
        //load image first ==v
        img.onload = function()
        {
            ctx.drawImage(img, 0, 0, size_x, size_y);
        };
        img.src = source;
    }
    else
    {
        ////console.log("canvas not found");
    }
}

draw_b(0, 0, canvas_for_drawing); //draw black on top of canvas



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
var isdraw = 0;
canvas_for_drawing.style.zIndex = "9";
canvas_for_drawing_square.style.zIndex = "8";

var drag = false;
var pos_sq_x = 0;
var pos_sq_y = 0;
var pos_sq_fx = 0;
var pos_sq_fy = 0;



function draw_mouse_affordances(tmp, canvas, canvas_sq, e)
{
    var context = canvas.getContext("2d");
    var context_sq = canvas_sq.getContext("2d");
    var pos = getMousePos(canvas, e);
    var pos_sq = getMousePos(canvas_sq, e);
    //var canvas_check = document.elementFromPoint(pos.x, pos.y);

    if(mouseDown)
    {   
        if (isrect)
        {
            if (firstlog == 1)
            {
                //canvas_for_drawing_square.style.zIndex = "10";
                canvas_for_drawing_square.style.zIndex = "10";
                ////console.log(pos_sq);
                rect_x1 = pos_sq.x;
                rect_y1 = pos_sq.y;
                firstlog = 0;
                drag = 1;
            }
            else 
            {
                if (drag == 1)
                {
                    rect_x2 = pos_sq.x;
                    rect_y2 = pos_sq.y;
                    context_sq.clearRect(0,0,canvas_sq.width,canvas_sq.height);
                    context_sq.fillStyle = "white";
                    context_sq.fillRect(rect_x1, rect_y1, ((rect_x2-rect_x1)+4), (rect_y2-rect_y1));
                }                
            }
        }
        //canvas_for_drawing_square.style.zIndex = "8";
        if (isdraw)
        {
            context.fillStyle = color;
            context.fillRect(pos.x - ((pos.x /*- grid_movex*/) % sizex), pos.y - ((pos.y /*- grid_movey*/) % sizey), sizex, sizey);
        }
    }
    if (!mouseDown)
    {
        if (isrect)
        {
            if (firstlog == 0)
            {
                if(event.button == 0)
                {
                    drag = 0;
                    //canvas_for_drawing_square.style.zIndex = "10";
                    ////console.log("finish");
                    rect_x2 = pos_sq.x;
                    rect_y2 = pos_sq.y;
                    firstlog = 1;
                    context_sq.clearRect(0,0,canvas_sq.width,canvas_sq.height);
                    context.fillStyle = "white";
                    context.fillRect(rect_x1, rect_y1, ((rect_x2-rect_x1)+4), (rect_y2-rect_y1));
                    ////console.log(canvas_for_drawing.toDataURL());
                    //context_sq.fillStyle = "white";
                    //context_sq.fillRect(rect_x1, rect_y1, ((rect_x2-rect_x1)+4), (rect_y2-rect_y1));
                }
            }
        }
    }
}
//var mouseOut = true;
canvas_for_drawing.onmouseover = function()
{
    //mouseOut = false;
    event.preventDefault();
        //mouseDown = 0;
        //mouseOut = false;
    mouseDown = 0;
    ////console.log(mouseDown);
}

canvas_for_drawing.onmouseout = function()
{
    event.preventDefault();
    //mouseOut = true;
    mouseDown = 0;
    ////console.log(mouseDown);
    //    return;         
}
canvas_for_drawing_square.onmouseover = function()
{
    //mouseOut = false;
    event.preventDefault();
        //mouseDown = 0;
        //mouseOut = false;
    mouseDown = 0;
    ////console.log(mouseDown);
}

canvas_for_drawing_square.onmouseout = function()
{
    event.preventDefault();
    //mouseOut = true;
    mouseDown = 0;
    
    //    return;         
}
    canvas_for_drawing.onmousedown = function()
    {
        event.preventDefault();
        if(event.button == 0)
        {
            mouseDown = 1;
            if (isrect)
            {
                //canvas_for_drawing_square.style.zIndex = "10";
                color = "rgba(255, 255, 255, 0)";
            }
            else
            {
                //canvas_for_drawing_square.style.zIndex = "8";
                color = "white";
            }       
        }
        if(event.button == 2)
        {
            mouseDown = 1;
            if (isrect)
            {
                //canvas_for_drawing_square.style.zIndex = "10";
                color = "rgba(0, 0, 0, 0)";;
            }
            else
            {
                //canvas_for_drawing_square.style.zIndex = "8";
                color = "black";
            }   
             
        }
    }
    canvas_for_drawing.onmouseup = function()
    {
        event.preventDefault();
        if(event.button == 0)
        {
            mouseDown = 0;
            if (isrect)
            {
                //canvas_for_drawing_square.style.zIndex = "10";
                color = "rgba(255, 255, 255, 1)";
            }
            else 
            {
                //canvas_for_drawing_square.style.zIndex = "8";
                color = "white";
            }
            
        }
        if(event.button == 2)
        {
            canvas_for_drawing_square.style.zIndex = "8";
            mouseDown = 0;
            color = "black";
        }
    }
    canvas_for_drawing_square.onmousedown = function()
    {
        ////console.log(mouseDown);
        event.preventDefault();
        if(event.button == 0)
        {
            mouseDown = 1;
            if (isrect)
            {
                //canvas_for_drawing_square.style.zIndex = "10";
                color = "rgba(255, 255, 255, 0)";
            }
            else
            {
                //canvas_for_drawing_square.style.zIndex = "8";
                color = "white";
            }       
        }
        if(event.button == 2)
        {
            mouseDown = 1;
            if (isrect)
            {
                //canvas_for_drawing_square.style.zIndex = "10";
                color = "rgba(0, 0, 0, 0)";;
            }
            else
            {
                //canvas_for_drawing_square.style.zIndex = "8";
                color = "black";
            }   
             
        }
    }
    canvas_for_drawing_square.onmouseup = function()
    {
        event.preventDefault();
        if(event.button == 0)
        {

            mouseDown = 0;
            if (isrect)
            {
                //canvas_for_drawing_square.style.zIndex = "10";
                color = "rgba(255, 255, 255, 1)";
            }
            else 
            {
                //canvas_for_drawing_square.style.zIndex = "8";
                color = "white";
            }
            
        }
        if(event.button == 2)
        {
            canvas_for_drawing_square.style.zIndex = "8";
            mouseDown = 0;
            color = "black";
        }
    }

    window.addEventListener('mousemove', draw_mouse_affordances.bind(null, event, canvas_for_drawing, canvas_for_drawing_square), false);
    window.addEventListener('mousedown', draw_mouse_affordances.bind(null, event, canvas_for_drawing, canvas_for_drawing_square), false);
    window.addEventListener('mouseover', draw_mouse_affordances.bind(null, event, canvas_for_drawing, canvas_for_drawing_square), false);
    window.addEventListener('mouseout', draw_mouse_affordances.bind(null, event, canvas_for_drawing, canvas_for_drawing_square), false);
    canvas_for_drawing.addEventListener('contextmenu', event => event.preventDefault());//block rightclick on 'em
    canvas_for_drawing_square.addEventListener('contextmenu', event => event.preventDefault());//block rightclick on 'em

//----------------------------------------------------------------------------

function getMousePos(canvas, evt)
{
    var rect = canvas.getBoundingClientRect();
    return {
        x: (evt.clientX - rect.left) / (rect.right - rect.left) * canvas.width,
        y: (evt.clientY - rect.top) / (rect.bottom - rect.top) * canvas.height
    };
};



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
    ////console.log('on load')
    fetch_data();
})

function fetch_data(){
  ////console.log('mydata first')
  ////console.log(mydata)
  temp_url = BASE_URL + "/expert/get_image?tagger=" + TAGGER_ID
  //$.getJSON(temp_url, function(json) original code 10/2020
  $.getJSON("/example_data.json", function(json)
  {
      mydata = json;
      ////console.log('mydata 2nd')
      ////console.log(mydata);
      ////console.log(mydata["output"]) // this will show the info it in firebug //console
      output =
      {
          "tagger_id":TAGGER_ID,
          "image_id":mydata.output.image_id
      };
      ////console.log('output w/ tagger')
      ////console.log(output)
      output["affordance_images"] =  
      {
        "solid": 0,
        "movable":0,
        "destroyable":0,
        "dangerous":0,
        "gettable":0,
        "portal":0,
        "usable":0,
        "changeable":0,
        "ui":0,
        "permeable":0
      }
      for (var index = 0; index < Object.keys(mydata["output"]['tiles']).length; index++) //was [output][tiles] originally
      {
          var texture_index = 'tile_' + index;
          var act_texture = mydata.output.tiles[texture_index];
          out_textures[texture_index] =
          {
              "tile_id": act_texture['tile_id'],
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
              "comment":""
          };
       }
       ////console.log(mydata)
       update_images()
  });
}

function update_images(){
    ////console.log(mydata["output"]['image'])
    ////console.log(mydata["output"]['solid'])
    var drawinn_img = document.getElementById('drawer');
    drawinn_img.src = mydata["output"]['image'];
    var scrn_img = document.getElementById('screenshot_preview');
    scrn_img.src = mydata["output"]['image'];
    var texture_tmp = document.getElementById('texture');
    texture_tmp.src = mydata["output"]['tiles']['tile_0']['tile_data'];
    document.getElementById("textures").textContent=String(num) + "/" + String(Object.keys(mydata["output"]['tiles']).length - 1) + " tiles";

    var poses = mydata["output"]['tiles']['tile_' + num]['locations'];
    for(i = 0; i < Object.keys(poses).length; i++)
    {
        pos_x = alt_posx(poses['location_' + i]['x'], canvas_for_drawing);
        pos_y = alt_posy(poses['location_' + i]['y'], canvas_for_drawing);
        draw(pos_x, pos_y, canvas_for_drawing);
    }
}

function send_output_to_server(){
    //console.log('Space pressed submitting')
    //console.log(output)
    var tmp_url = BASE_URL + "/api/insert"
    $.ajax({
      url: tmp_url,
      type: "post",
      data: JSON.stringify(output),
      contentType: "application/json",
      success: function (data) {
        ////console.log('Sent labels to server /submit_tags')
        ////console.log(data)
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
function alt_posx(pos, canv)
{
    var tmp = pos/256;
    pos = tmp*canv.width;
    return pos;
}
function alt_posy(pos, canv)
{
    var tmp = pos/224;
    pos = tmp*canv.height;
    return pos;
}


function flip_affordance(whichcheckbox, whichcanvas){
    ////console.log("flip_canvas");
    ////console.log(whichcanvas)
    var aff = whichcheckbox.getAttribute("aff");
    if(!whichcheckbox.checked)
    {
        //mydata["output"]['tiles']['tile_' + num]['locations'];
        var poses = mydata["output"]['tiles']['tile_' + num]['locations'];
        for(i = 0; i < Object.keys(poses).length; i++)
        {
            pos_x = poses['location_' + i]['x'];
            pos_x = alt_posx(pos_x, whichcanvas);
            pos_y = poses['location_' + i]['y'];
            pos_y = alt_posy(pos_y, whichcanvas);
            draw_b(pos_x, pos_y, whichcanvas);
            
        }
        out_textures["tile_" + num][aff] = 0;
    }
    else{
        var poses = mydata["output"]['tiles']['tile_' + num]['locations'];
        for(i = 0; i < Object.keys(poses).length; i++)
        {
            pos_x = poses['location_' + i]['x'];
            pos_x = alt_posx(pos_x, whichcanvas);
            pos_y = poses['location_' + i]['y'];
            pos_y = alt_posy(pos_y, whichcanvas);
            draw(pos_x, pos_y, whichcanvas);
        }   
            out_textures["tile_" + num][aff] = 1;
    }
    ////console.log(whichcanvas.toDataURL());
    ////console.log("flipped");
}




function saveAffordanceImages(tilenum){

    output["affordance_images"] =  
    {
        'dangerous': document.getElementById("myCanvas_drawing1").toDataURL(),
        'solid': document.getElementById("myCanvas_drawing2").toDataURL(),
        'permeable': document.getElementById("myCanvas_drawing3").toDataURL(),
        'changeable': document.getElementById("myCanvas_drawing4").toDataURL(),
        'movable': document.getElementById("myCanvas_drawing5").toDataURL(),
        'destroyable': document.getElementById("myCanvas_drawing6").toDataURL(),
        'gettable': document.getElementById("myCanvas_drawing7").toDataURL(),
        'usable': document.getElementById("myCanvas_drawing8").toDataURL(),
        'portal': document.getElementById("myCanvas_drawing9").toDataURL(),
        'ui': document.getElementById("myCanvas_drawing10").toDataURL()
    }
    //console.log('saved to output[tagimages]')
    ////console.log(output);
    
}
var prev_canvas = null;
function goDraw(whichcheckbox)
{
    if(prev_canvas != null)
    {
        output["affordance_images"][prev_canvas.getAttribute("aff")] = canvas_for_drawing.toDataURL();
        //console.log(output["affordance_images"][prev_canvas.getAttribute("aff")]);
        //console.log("output draw");
        //console.log(output);
        ////console.log(output["affordance_images"][prev_canvas.getAttribute("aff")]);
    }
    if(whichcheckbox.checked)
    {
        var affo = whichcheckbox.getAttribute("aff");
        for (var i = 0; i < cb_list.length; i++)
        {
            cb_list[i].checked = false;
        }
        whichcheckbox.checked = true;
        ////console.log(whichcheckbox)
        erase(canvas_for_drawing);
        draw_b(0, 0, canvas_for_drawing);
        draw_picture(output["affordance_images"][affo], canvas_for_drawing, canvas_for_drawing.width, canvas_for_drawing.height);
        prev_canvas = whichcheckbox;
        ////console.log(output);
        //saveAffordanceImages();
        
    }
}

var out_of_num = 0;
var end_of_tagging = false;

function FindByAttributeValue(attribute, value, element_type)    {
    element_type = element_type || "*";
    var All = document.getElementsByTagName(element_type);
    for (var i = 0; i < All.length; i++)       {
      if (All[i].getAttribute(attribute) == value) { return All[i]; }
    }
  }

document.onkeydown = function(event)
{
    var pos_x = 0;
    var pos_y = 0;
    var textures = mydata["output"]['tiles'];
    var poses = mydata["output"]['tiles']['tile_' + num]['locations'];
    switch (event.keyCode)
    {
        case 162: //Backspace
                erase(canvas_for_drawing);
                draw_b(0, 0, myCanvas_drawing);
                for (var i = 0; i < 10; i++)
                {
                    cb_list[i].checked = false;
                }
                if (end_of_tagging == false)
                {
                    if (num > 0)
                    {
                        num = num - 1;
                    }
                    else
                    {
                            alert('Out of textures. Current texture num = ' + num);
                    }
                    document.getElementById("my_comment").value = out_textures["tile_"+num]['comment'];
                    //console.log(out_textures["tile_"+num]['comment']);
                }
                
                texture.src = textures['tile_' + num]['tile_data'];
                poses = mydata["output"]['tiles']['tile_' + num]['locations'];

                for(i = 0; i < Object.keys(poses).length; i++)
                {
                    pos_x = poses['location_' + i]['x'];
                    pos_x = alt_posx(pos_x, canvas_for_drawing);
                    pos_y = poses['location_' + i]['y'];
                    pos_y = alt_posy(pos_y, canvas_for_drawing);
                    draw(pos_x, pos_y, canvas_for_drawing);
                }
                //checkboxes_____________________________________________________
                var text_tmp = out_textures["tile_" + num];
                for (var i = 0 in text_tmp)
                {
                    if (text_tmp[i] == 1)
                    {
                        FindByAttributeValue("aff", i).checked = true;
                    }
                }
                saveAffordanceImages();
                document.getElementById("textures").textContent=String(num) + "/" + String(Object.keys(mydata["output"]['tiles']).length - 1) + " tiles";
        break;
        case 27:
            closeInstr();
        break;    
        case 165: //ENTER
            if (end_of_tagging == false)
            {
                //console.log(num);
                erase(canvas_for_drawing);
                draw_b(0, 0, myCanvas_drawing);
                for (var i = 0; i < 10; i++)
                {
                    cb_list[i].checked = false;
                }
                out_textures["tile_"+num]['comment'] = document.querySelector('.comment_class').value;
                document.querySelector('.comment_class').value = '';
                num = num + 1;
                if (num == (Object.keys(textures).length))//check evr time that num doesnt exceed amount of textures
                {
                    num = num - 1;
                    alert('Out of tiles. You may now proceed to draw of continue tagging');
                    button_done.disabled = false;
                }
                
                texture.src = textures['tile_' + num]['tile_data'];
                poses = mydata["output"]['tiles']['tile_' + num]['locations'];
                //drawGrid(canvas_draw, 256, 224, GRID_SIZE, 'rgb(250, 25, 25)')
                for(i = 0; i < Object.keys(poses).length; i++)
                {
                    pos_x = poses['location_' + i]['x'];
                    pos_x = alt_posx(pos_x, canvas_for_drawing);
                    pos_y = poses['location_' + i]['y'];
                    pos_y = alt_posy(pos_y, canvas_for_drawing);
                    draw(pos_x, pos_y, canvas_for_drawing);
                }
                saveAffordanceImages();
                var text_tmp = out_textures["tile_" + num];
                for (var i = 0 in text_tmp)
                {
                    if (text_tmp[i] == 1)
                    {
                        FindByAttributeValue("aff", i).checked = true;
                    }
                }
                
                //console.log(out_textures[num]["comment"]);
                document.getElementById("textures").textContent = String(num) + "/" + String(Object.keys(mydata["output"]['tiles']).length - 1) + " tiles";
            }
        break;
            //__________________________________________________________
        case 1000: //space to save
            if (end_of_tagging == false)
            {
                saveAffordanceImages();
                output["tiles"] = out_textures;
                out_tmp = output;
                end_of_tagging = true;
                button_back.disabled = true;
                button_next.disabled = true;
                button_square.disabled = false;
                button_draw.disabled = false;
            }
            else 
            {
                console.log("opp")
                console.log(output);
                send_output_to_server();
            }
            
        break;
    }
}
