var _arlec_yes = document.getElementById("yes")
_arlec_yes.onchange = function(){
if (this.checked){
send_request("On")
}
}
var _arlec_no = document.getElementById("no")
_arlec_no.onchange = function(){
if (this.checked){
send_request("Off")
}
}
async function send_request(state){
await fetch('?{"command":"set_value","endpoint_id":"<<ENDPOINT_ID>>","attributes":"{""Power"":""' + state + '""}"}').then(response => response.json()).then(response => {
refresh_arlec_select(response["attributes"]["Power"])
})}
function refresh_arlec_select(power_arlec_selected_value){
var power_arlec_On = document.getElementById("yes")
var power_arlec_Off = document.getElementById("no")
if (power_arlec_selected_value == "On"){
power_arlec_On.checked = true
} else {
power_arlec_Off.checked = true
}
}
window.addEventListener("DOMContentLoaded", refresh_arlec_select("<<POWER>>"), false)
