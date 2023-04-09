async function refresh_temp_sensor(){
await fetch('?{"command":"get_value","endpoint_id":<<ENDPOINT_ID>>,"attributes":["Temp"]}').then(response => response.json()).then(response => {
var temp_sensor_info_id = document.getElementById("temp_sensor_info1")
temp_sensor_info_id.innerHTML = response["attributes"]["Temp"] + "&deg;C"
var temp_sensor_last_refresh_id = document.getElementById("temp_sensor_last_refresh")
const currentDate = new Date()
temp_sensor_last_refresh_id.innerHTML = "Last refresh: " + currentDate.getFullYear() + "-" + (currentDate.getMonth()+1) + "-" + 
currentDate.getDay() + " " + currentDate.getHours() + ":" + currentDate.getMinutes() + ":" + currentDate.getSeconds() + 
"; Tap to refresh again"
})
}
window.addEventListener("DOMContentLoaded", refresh_temp_sensor, false)
