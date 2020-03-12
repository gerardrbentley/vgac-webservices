/*

██████╗░███████╗░██████╗██╗░██████╗░███╗░░██╗
██╔══██╗██╔════╝██╔════╝██║██╔════╝░████╗░██║
██║░░██║█████╗░░╚█████╗░██║██║░░██╗░██╔██╗██║
██║░░██║██╔══╝░░░╚═══██╗██║██║░░╚██╗██║╚████║
██████╔╝███████╗██████╔╝██║╚██████╔╝██║░╚███║
╚═════╝░╚══════╝╚═════╝░╚═╝░╚═════╝░╚═╝░░╚══╝
───────────────────────────────────────────────────────────────────────────────────────────────
─████████████───██████████████─██████████████─██████████─██████████████─██████──────────██████─
─██░░░░░░░░████─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░██─██░░░░░░░░░░██─██░░██████████──██░░██─
─██░░████░░░░██─██░░██████████─██░░██████████─████░░████─██░░██████████─██░░░░░░░░░░██──██░░██─
─██░░██──██░░██─██░░██─────────██░░██───────────██░░██───██░░██─────────██░░██████░░██──██░░██─
─██░░██──██░░██─██░░██████████─██░░██████████───██░░██───██░░██─────────██░░██──██░░██──██░░██─
─██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██───██░░██───██░░██──██████─██░░██──██░░██──██░░██─
─██░░██──██░░██─██░░██████████─██████████░░██───██░░██───██░░██──██░░██─██░░██──██░░██──██░░██─
─██░░██──██░░██─██░░██─────────────────██░░██───██░░██───██░░██──██░░██─██░░██──██░░██████░░██─
─██░░████░░░░██─██░░██████████─██████████░░██─████░░████─██░░██████░░██─██░░██──██░░░░░░░░░░██─
─██░░░░░░░░████─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░██─██░░░░░░░░░░██─██░░██──██████████░░██─
─████████████───██████████████─██████████████─██████████─██████████████─██████──────────██████─
───────────────────────────────────────────────────────────────────────────────────────────────
*/
var pos_x = 0;
var pos_y = 0;

/*
var c = document.getElementById("canvas_tile");
var ctx = c.getContext("2d");

ctx.beginPath();
ctx.arc(289, 289, 288, 0, 180);
ctx.strokeStyle = "rgb(113, 244, 244)";
ctx.stroke();
ctx.fillStyle = "rgb(113, 244, 244)";
ctx.fill();
*/

//console.log(solid_dot);

var solid_dot = document.getElementById("dot_solid");
var solid_counter = 0;
var b_solid = document.getElementById("b_solid");
//b_solid.style.backgroundColor = "#ff66ff";
b_solid.style.fontSize = "x-large";
b_solid.style.fontVariant = "small-caps";
b_solid.onclick = function()
{
    
    update_output("solid", solid_counter);
    update_button(b_solid);
};

var movable_dot = document.getElementById("dot_movable");
var movable_counter = 0;
var b_movable = document.getElementById("b_movable");
//b_movable.style.backgroundColor = "#ff66ff";
b_movable.style.fontSize = "x-large";
b_movable.style.fontVariant = "small-caps";
b_movable.onclick = function()
{
    update_output("movable", movable_counter);
    update_button(b_movable);
};

var destroyable_dot = document.getElementById("dot_destroyable");
var destroyable_counter = 0;
var b_destroyable = document.getElementById("b_destroyable");
//b_destroyable.style.backgroundColor = "#ff66ff";
b_destroyable.style.fontSize = "x-large";
b_destroyable.style.fontVariant = "small-caps";
b_destroyable.onclick = function()
{
    update_output("destroyable", destroyable_counter);
    update_button(b_destroyable);
};

var dangerous_dot = document.getElementById("dot_dangerous");
var dangerous_counter = 0;
var b_dangerous = document.getElementById("b_dangerous");
//b_dangerous.style.backgroundColor = "#ff66ff";
b_dangerous.style.fontSize = "x-large";
b_dangerous.style.fontVariant = "small-caps";
b_dangerous.onclick = function()
{
    update_output("dangerous", dangerous_counter);
    update_button(b_dangerous);
};

var gettable_dot = document.getElementById("dot_gettable");
var gettable_counter = 0;
var b_gettable = document.getElementById("b_gettable");
//b_gettable.style.backgroundColor = "#ff66ff";
b_gettable.style.fontSize = "x-large";
b_gettable.style.fontVariant = "small-caps";
b_gettable.onclick = function()
{
    update_output("gettable", gettable_counter);
    update_button(b_gettable);
};

var portal_dot = document.getElementById("dot_portal");
var portal_counter = 0;
var b_portal = document.getElementById("b_portal");
//b_portal.style.backgroundColor = "#ff66ff";
b_portal.style.fontSize = "x-large";
b_portal.style.fontVariant = "small-caps";
b_portal.onclick = function()
{
    update_output("portal", portal_counter);
    update_button(b_portal);
};

var usable_dot = document.getElementById("dot_usable");
var usable_counter = 0;
var b_usable = document.getElementById("b_usable");
//b_usable.style.backgroundColor = "#ff66ff";
b_usable.style.fontSize = "x-large";
b_usable.style.fontVariant = "small-caps";
b_usable.onclick = function()
{
    update_output("usable", usable_counter);
    update_button(b_usable);
};

var changeable_dot = document.getElementById("dot_changeable");
var changeable_counter = 0;
var b_changeable = document.getElementById("b_changeable");
//b_changeable.style.backgroundColor = "#ff66ff";
b_changeable.style.fontSize = "x-large";
b_changeable.style.fontVariant = "small-caps";
b_changeable.onclick = function()
{
    update_output("changeable", changeable_counter);
    update_button(b_changeable);
};

var ui_dot = document.getElementById("dot_ui");
var ui_counter = 0;
var b_ui = document.getElementById("b_ui");
//b_ui.style.backgroundColor = "#ff66ff";
b_ui.style.fontSize = "x-large";
b_ui.style.fontVariant = "small-caps";
b_ui.onclick = function()
{
    update_output("ui", ui_counter);
    update_button(b_ui);
};

var permeable_dot = document.getElementById("dot_permeable");
var permeable_counter = 0;
var b_permeable = document.getElementById("b_permeable");
//b_permeable.style.backgroundColor = "#ff66ff";
b_permeable.style.fontSize = "x-large";
b_permeable.style.fontVariant = "small-caps";
b_permeable.onclick = function()
{
    update_output("permeable", permeable_counter);
    update_button(b_permeable);
};

var b_save = document.getElementById("b_save");
b_save.style.backgroundColor = "rgb(131,58,180)";
b_save.style.fontSize = "x-large";
b_save.style.fontVariant = "small-caps";
b_save.onclick = function()
{
    alert("Save susccessul");
};

var b_comment = document.getElementById("b_comment");
b_comment.style.backgroundColor = "rgb(131,58,180)";
b_comment.style.fontSize = "x-large";
b_comment.style.fontVariant = "small-caps";


var b_context = document.getElementById("b_context");
b_context.style.backgroundColor = "rgb(6,100,105)";
b_context.style.fontSize = "x-large";
b_context.style.fontVariant = "small-caps";

var canvas_drawinn = document.getElementById("myCanvas_drawing");
b_context.onclick = function()
{
    poses = mydata["output"]["tile"]["locations"];
    for(i = 0; i < Object.keys(poses).length; i++)
    {
        pos_x = poses['location_' + i]['x'];
        pos_y = poses['location_' + i]['y'];
        console.log(pos_x);
        console.log(pos_y);
        draw(pos_x, pos_y, canvas_drawinn);
    }
    drawer.src = mydata["output"]["image"];
    drawinn.style.display = "block";
};



var bClose = document.getElementById("bClose");
bClose.onclick = function()
{
    drawinn.style.display = "none";
};

var b_reset = document.getElementById("b_reset");
b_reset.style.backgroundColor = "rgb(6,100,105)";
b_reset.style.fontSize = "x-large";
b_reset.style.fontVariant = "small-caps";
b_reset.onclick = function()
{
  alert("reset successful!");
  output["solid"] = 0;
  output["movable"] = 0;
  output["destroyable"] = 0;
  output["dangerous"] = 0;
  output["gettable"] = 0;
  output["portal"] = 0;
  output["usable"] = 0;
  output["changeable"] = 0;
  output["ui"] = 0;
  output["permeable"] = 0;
 
};

/*

─────────────────────────────────────────────────────────────────────────────────────────────────────────────
─██████████████─██████████████─██████████████────████████████───██████████████─██████████████─██████████████─
─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██────██░░░░░░░░████─██░░░░░░░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░██████████─██░░██████████─██████░░██████────██░░████░░░░██─██░░██████░░██─██████░░██████─██░░██████░░██─
─██░░██─────────██░░██─────────────██░░██────────██░░██──██░░██─██░░██──██░░██─────██░░██─────██░░██──██░░██─
─██░░██─────────██░░██████████─────██░░██────────██░░██──██░░██─██░░██████░░██─────██░░██─────██░░██████░░██─
─██░░██──██████─██░░░░░░░░░░██─────██░░██────────██░░██──██░░██─██░░░░░░░░░░██─────██░░██─────██░░░░░░░░░░██─
─██░░██──██░░██─██░░██████████─────██░░██────────██░░██──██░░██─██░░██████░░██─────██░░██─────██░░██████░░██─
─██░░██──██░░██─██░░██─────────────██░░██────────██░░██──██░░██─██░░██──██░░██─────██░░██─────██░░██──██░░██─
─██░░██████░░██─██░░██████████─────██░░██────────██░░████░░░░██─██░░██──██░░██─────██░░██─────██░░██──██░░██─
─██░░░░░░░░░░██─██░░░░░░░░░░██─────██░░██────────██░░░░░░░░████─██░░██──██░░██─────██░░██─────██░░██──██░░██─
─██████████████─██████████████─────██████────────████████████───██████──██████─────██████─────██████──██████─
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
*/

//vars
var drawinn = document.getElementById("drawing_container");
var canvas_drawinn = document.getElementById("myCanvas_drawing");
drawinn.style.display = "none";
var drawer = document.getElementById("drawer");
const GRID_SIZE = 8;
var counter_button = 0;



var tagger_id = "test";
var mydata = {};
var output = {};

const baseURL = window.location
console.log(baseURL.href)
const basePathArray = baseURL.pathname.split('/')
console.log(basePathArray)
console.log(basePathArray[1])
var BASE_URL = ''
if (basePathArray[1] === 'staging')
{
     console.log('staging site')
     BASE_URL = '/staging'
}
else
{
     console.log('live site')
}

var $ = window.jQuery;
window.addEventListener('load', function()
{
    console.log('on load')
    output["solid"] = 0;
    output["movable"] = 0;
    output["destroyable"] = 0;
    output["dangerous"] = 0;
    output["gettable"] = 0;
    output["portal"] = 0;
    output["usable"] = 0;
    output["changeable"] = 0;
    output["ui"] = 0;
    output["permeable"] = 0;
    fetch_data();
});



function fetch_data(){
  
  //tagger_id = document.getElementById("tagger_id").getAttribute('tagger')
  temp_url = BASE_URL + "/single-tile/get_image?tagger=" + tagger_id
  $.getJSON(temp_url, function(json)
  //$.getJSON("example_data.json", function(json) 
  {
      mydata = json;
      output = //get tagger id from somewhere later (?)
      {
          "tagger_id":tagger_id,
          "tile_id":mydata.output.tile.tile_id,
          "tile_data":mydata.output.tile.tile_data,
          "solid":0,
          "movable":0,
          "destroyable":0,
          "dangerous":0,
          "gettable":0,
          "portal":0,
          "usable":0,
          "changeable":0,
          "ui":0,
          "permeable":0
      };
      console.log('output w/ tagger')
      console.log(output)
      //console.log(act_tile);
      update_tile()
  });
//   setTimeout(function() {update_tile()}, 200);
}


function update_tile()
{
  
  console.log('update_tile')
  console.log(output);
  var tile_img = document.getElementById("tile_now");
  tile_img.src = output['tile_data'];
}

function openNav() 
{
  document.getElementById("mySidenav").style.width = "250px";
}

/* Set the width of the side navigation to 0 */
function closeNav() 
{
  document.getElementById("mySidenav").style.width = "0";
}


function closeInstr() 
{
  document.getElementById("myInstructions").style.width = "0";
}


function update_output(affordance, counter)
{
    output[affordance] = counter+0.5;
    console.log("output = ");
    console.log(output[affordance]);
}

function update_button(name)
{
    window[name.value+"_counter"] += 0.5;
    //console.log(window[name.value+"_counter"]);
    console.log(window[name.value+"_dot"]);
    if (window[name.value+"_counter"] == 0)
    {
        window[(name.value+"_dot")].style.backgroundColor = "red";
    }
    else if (window[name.value+"_counter"] == 0.5)
    {
         window[(name.value+"_dot")].style.backgroundColor = "yellow";
    }
    else 
    {
        window[name.value+"_counter"] = -0.5;
        window[(name.value+"_dot")].style.backgroundColor = "green";
    }
    
}


function draw(x, y, z)
{

    if (z.getContext)
    {
        var ctx = z.getContext('2d');
        ctx.strokeStyle = 'rgb(255,255,  255)';
        ctx.lineWidth = 10;
        ctx.strokeRect(x, y, GRID_SIZE, GRID_SIZE)
    }
}


function comment() 
{
    var cmt = prompt("Please enter your comment here", "");
    if (cmt != null) 
    {
      //save here
      alert("Saved");
    }
}