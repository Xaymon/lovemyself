var a;
function show_exo(){
    if(a==1){
        document.getElementById("exo").style.display="inline";
        document.getElementById("aespa").style.display="none";
        document.getElementById("fx").style.display="none";
        document.getElementById("shinee").style.display="none";
        return a=0;
    }
    else{
        document.getElementById("exo").style.display="inline";
        document.getElementById("aespa").style.display="none";
        document.getElementById("fx").style.display="none";
        document.getElementById("shinee").style.display="none";
        return a=1;
    }
}

var b;
function show_aespa(){
    if(b==1){
        document.getElementById("exo").style.display="none";
        document.getElementById("aespa").style.display="inline";
        document.getElementById("fx").style.display="none";
        document.getElementById("shinee").style.display="none";
        return b=0;
    }
    else{
        document.getElementById("exo").style.display="none";
        document.getElementById("aespa").style.display="inline";
        document.getElementById("fx").style.display="none";
        document.getElementById("shinee").style.display="none";
        return b=1;
    }
}

var c;
function show_fx(){
    if(c==1){
        document.getElementById("exo").style.display="none";
        document.getElementById("aespa").style.display="none";
        document.getElementById("fx").style.display="inline";
        document.getElementById("shinee").style.display="none";
        return c=0;
    }
    else{
        document.getElementById("exo").style.display="none";
        document.getElementById("aespa").style.display="none";
        document.getElementById("fx").style.display="inline";
        document.getElementById("shinee").style.display="none";
        return c=1;
    }
}

var d;
function show_shinee(){
    if(d==1){
        document.getElementById("exo").style.display="none";
        document.getElementById("aespa").style.display="none";
        document.getElementById("fx").style.display="none";
        document.getElementById("shinee").style.display="inline";
        return d=0;
    }
    else{
        document.getElementById("exo").style.display="none";
        document.getElementById("aespa").style.display="none";
        document.getElementById("fx").style.display="none";
        document.getElementById("shinee").style.display="inline";
        return d=1;
    }
}