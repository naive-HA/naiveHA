function naiveHA_temp_sensor_addZero(number) {
    if (number < 10) {
        number = '0' + number
    }
    return number
}
async function naiveHA_temp_sensor_refresh() {
    document.getElementById("naiveHA_temp_sensor_info").style.color = "gray"
    await fetch('?{"command":"get_value","endpoint_id":<<ENDPOINT_ID>>,"attributes":"[""Temp""]"}').then(response => response.json()).then(response => {
        var temp_sensor_info_id = document.getElementById("naiveHA_temp_sensor_info")
        var temp = "" + response["attributes"]["Temp"]
        if (temp.indexOf(".") < 0) {
            temp += ".0"
        }
        temp_sensor_info_id.innerHTML = temp + "&deg;C"
        document.getElementById("naiveHA_temp_sensor_info").style.color = ""
        var temp_sensor_last_refresh_id = document.getElementById("naiveHA_temp_sensor_last_refresh")
        const currentDate = new Date()
        temp_sensor_last_refresh_id.innerHTML = "Last refresh: " + currentDate.getFullYear() + "-" + naiveHA_temp_sensor_addZero(currentDate.getMonth() + 1) + "-" +
            naiveHA_temp_sensor_addZero(currentDate.getDay()) + " " + naiveHA_temp_sensor_addZero(currentDate.getHours()) + ":" + 
            naiveHA_temp_sensor_addZero(currentDate.getMinutes()) + ":" + naiveHA_temp_sensor_addZero(currentDate.getSeconds()) +
            "; Tap to refresh again"
    })
}
window.addEventListener("DOMContentLoaded", naiveHA_temp_sensor_refresh, false)
