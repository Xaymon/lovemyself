//function random_imglink(){
//var myimages=new Array()
////specify random images below. You can have as many as you wish
//myimages[1]="Merry/R_suho.png"
//myimages[2]="Merry/R_beakhyun.png"
//myimages[3]="Merry/R_chanyeol.png"
//myimages[4]="Merry/R_DO.png"
//myimages[5]="Merry/R_kai.png"
//myimages[6]="Merry/R_sehun.png"
//
//var number=Math.floor(Math.random()*myimages.length)
//if (number==0)
//number=1
//document.write('<img class="R_Card_EXO590" src="'+myimages[number]+'" border=0>')
//}
//random_imglink()



var num = 0;
num = Math.floor(Math.random() * 100);
    //Normal 
    if (num < 17) {
        var images = [],
        index = 0;
images[0] = "<img src='icy/r_nong.png' class='R_Card_EXO590'>";
images[1] = "<img src='icy/r_da.png' class='R_Card_EXO590'>";
images[2] = "<img src='icy/r_may.png' class='R_Card_EXO590'>";
images[3] = "<img src='icy/r_kouang.png' class='R_Card_EXO590'>";
index = Math.floor(Math.random() * images.length);
  document.write(images[index]);
    }

    if (num < 33 && num > 16) {
        var images = [],
        index = 0;
images[0] = "<img src='icy/r_nong.png' class='R_Card_EXO590'>";
images[1] = "<img src='icy/r_da.png' class='R_Card_EXO590'>";
images[2] = "<img src='icy/r_may.png' class='R_Card_EXO590'>";
images[3] = "<img src='icy/r_kouang.png' class='R_Card_EXO590'>";
index = Math.floor(Math.random() * images.length);
  document.write(images[index]);
    }

    if (num < 49 && num > 32) {
        var images = [],
        index = 0;
images[0] = "<img src='icy/r_nong.png' class='R_Card_EXO590'>";
images[1] = "<img src='icy/r_da.png' class='R_Card_EXO590'>";
images[2] = "<img src='icy/r_may.png' class='R_Card_EXO590'>";
images[3] = "<img src='icy/r_kouang.png' class='R_Card_EXO590'>";
index = Math.floor(Math.random() * images.length);
  document.write(images[index]);
    }

    if (num < 65 && num > 48) {
        var images = [],
        index = 0;
images[0] = "<img src='icy/r_nong.png' class='R_Card_EXO590'>";
images[1] = "<img src='icy/r_da.png' class='R_Card_EXO590'>";
images[2] = "<img src='icy/r_may.png' class='R_Card_EXO590'>";
images[3] = "<img src='icy/r_kouang.png' class='R_Card_EXO590'>";
index = Math.floor(Math.random() * images.length);
  document.write(images[index]);
    }

    if (num < 81 && num > 64) {
        var images = [],
        index = 0;
images[0] = "<img src='icy/r_nong.png' class='R_Card_EXO590'>";
images[1] = "<img src='icy/r_da.png' class='R_Card_EXO590'>";
images[2] = "<img src='icy/r_may.png' class='R_Card_EXO590'>";
images[3] = "<img src='icy/r_kouang.png' class='R_Card_EXO590'>";
index = Math.floor(Math.random() * images.length);
  document.write(images[index]);
    }

    if (num < 97 && num > 80) {
        var images = [],
        index = 0;
images[0] = "<img src='icy/r_nong.png' class='R_Card_EXO590'>";
images[1] = "<img src='icy/r_da.png' class='R_Card_EXO590'>";
images[2] = "<img src='icy/r_may.png' class='R_Card_EXO590'>";
images[3] = "<img src='icy/r_kouang.png' class='R_Card_EXO590'>";
index = Math.floor(Math.random() * images.length);
  document.write(images[index]);
    }

    if (num > 96 && num < 100) {
        var images = [],
        index = 0;
images[0] = "<img src='icy/r_nong.png' class='R_Card_EXO590'>";
images[1] = "<img src='icy/r_da.png' class='R_Card_EXO590'>";
images[2] = "<img src='icy/r_may.png' class='R_Card_EXO590'>";
images[3] = "<img src='icy/r_kouang.png' class='R_Card_EXO590'>";
index = Math.floor(Math.random() * images.length);
  document.write(images[index]);
    }





var d;
function changecolor(){
    if(d==1){
        document.getElementById("equip").style.backgroundColor="#d7d9d6";
        document.getElementById("equip").style.color="#878988";
        return d=0;
    }
    else{
        document.getElementById("equip").style.backgroundColor="#d7d9d6";
        document.getElementById("equip").style.color="#878988";
        return d=1;
    }
}

var f;
function hide_o3(){
    if(f==1){
        document.getElementById("framecard").style.display="none";
        document.getElementById("all_o3").style.display="none";
        document.getElementById("successful").style.display="inline";
        return f=0;
    }
    else{
        document.getElementById("framecard").style.display="none";
        document.getElementById("all_o3").style.display="none";
        document.getElementById("successful").style.display="inline";
        return f=1;
    }
}




var bleep = new Audio();
    bleep.src = "openpremium.a.mp3";
var bleep2 = new Audio();
    bleep2.src = "decide.a.mp3";
var bleep3 = new Audio();
    bleep3.src = "cardreceive.a.mp3";
var bleep4 = new Audio();
    bleep4.src = "equip.a.mp3";