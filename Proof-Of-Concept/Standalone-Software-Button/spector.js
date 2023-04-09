var s_p = "<<POWER>>"
var s_h = "<<HEAT_LEVEL>>"
var s_f = "<<FAN>>"
var s_t = "<<TEMP>>"
var fetching = false

async function spector_p(p){
    if (!fetching){
        fetching = true
        s_p = p
        spector_refresh(s_p, s_h, s_f, s_t)
        await spector_fectch(s_p, s_h, s_f, s_t)
        fetching = false
    }
}
async function spector_h(h){
    if (!fetching){
        fetching = true
        s_h = h
        spector_refresh(s_p, s_h, s_f, s_t)
        await spector_fectch(s_p, s_h, s_f, s_t)
        fetching = false
    }
}
async function spector_f(f){
    if (!fetching){
        fetching = true
        s_f = f
        spector_refresh(s_p, s_h, s_f, s_t)
        await spector_fectch(s_p, s_h, s_f, s_t)
        fetching = false
    }
}
async function spector_t(t){
    if (!fetching){
        fetching = true
        s_t = t
        spector_refresh(s_p, s_h, s_f, s_t)
        await spector_fectch(s_p, s_h, s_f, s_t)
        fetching = false
    }
}
async function spector_fectch(p, h, f, t){
    await fetch('?{"command":"set_value","endpoint_id":"<<ENDPOINT_ID>>","attributes":"{""Power"":""' + p + '"",""HeatLevel"":""' + h + '"",""Fan"":""' + f + '"",""Temp"":""'+ t + '""}"}').then(response => response.json()).then(response => {
        s_p = response["attributes"]["Power"]
        s_h = response["attributes"]["HeatLevel"]
        s_f = response["attributes"]["Fan"]
        s_t = response["attributes"]["Temp"]
        spector_refresh(s_p, s_h, s_f, s_t)
    })
}
function spector_refresh(p, h, f, t){
    if (p == "Off"){
        document.getElementById("S_T_CAROUSEL").scrollLeft = 0
        document.getElementById("S_P_On").classList.remove("s_selected")
        document.getElementById("S_P_Off").classList.add("s_selected")
    } else {
        document.getElementById("S_P_On").classList.add("s_selected")
        document.getElementById("S_P_Off").classList.remove("s_selected")
    }
    document.getElementById("S_H_"+h).classList.add("s_selected")
    for (let i=1; i<5; i++){
        if (i!=parseInt(h)){
            document.getElementById("S_H_"+i).classList.remove("s_selected")
        }
    }
    if (f == "Off"){
        document.getElementById("S_F_On").classList.remove("s_selected")
        document.getElementById("S_F_Off").classList.add("s_selected")
    } else {
        document.getElementById("S_F_On").classList.add("s_selected")
        document.getElementById("S_F_Off").classList.remove("s_selected")
    }
    document.getElementById("S_T_"+t).classList.add("s_selected")
    for (let i=5; i<38; i++){
        if (i!=parseInt(t)){
            document.getElementById("S_T_"+i).classList.remove("s_selected")
        }
    }
}
window.addEventListener("DOMContentLoaded", spector_refresh(s_p, s_h, s_f, s_t), false)
