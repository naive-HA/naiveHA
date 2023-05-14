var naiveHA_temp_control_status = "<<CONTROLLER_STATUS>>"
var naiveHA_temp_control_heater_status = "<<HEATER_STATUS>>"
var naiveHA_temp_control_fan_status = "<<FAN_STATUS>>"
var naiveHA_temp_control_target_temp = "<<TARGET_TEMP>>"
var naiveHA_temp_control_room_temp = "<<ROOM_TEMP>>"
var naiveHA_temp_control_control_band = "<<CONTROL_BAND>>"
var naiveHA_temp_control_fetching = false
function naiveHA_temp_control_addZero(number) {
    if (number < 10) {
        number = '0' + number
    }
    return number
}
function naiveHA_temp_control_string_zero(number) {
    str_number = String(number)
    if (str_number.indexOf(".") < 0){
        str_number = number + ".0"
    }
    return str_number
}        
function naiveHA_temp_control_show_target_panel() {
    document.getElementById("info_panel").style.display = "none"
    document.getElementById("target_panel").style.display = "block"
}
function naiveHA_temp_control_show_info_panel() {
    document.getElementById("target_panel").style.display = "none"
    document.getElementById("info_panel").style.display = "block"
}
function naiveHA_temp_control_status_refresh() {
    naiveHA_temp_control_fetch("get_value", naiveHA_temp_control_status, naiveHA_temp_control_heater_status, naiveHA_temp_control_fan_status, 
    naiveHA_temp_control_target_temp, naiveHA_temp_control_room_temp, naiveHA_temp_control_control_band)
}
document.getElementById("naiveHA_temp_control_switch_activate").onchange = function () {
    if (!naiveHA_temp_control_fetching && this.checked) {
        naiveHA_temp_control_fetching = true
        naiveHA_temp_control_fetch("set_value", "Off", naiveHA_temp_control_heater_status, naiveHA_temp_control_fan_status, 
            naiveHA_temp_control_target_temp, naiveHA_temp_control_room_temp, naiveHA_temp_control_control_band)
    }
}
document.getElementById("naiveHA_temp_control_switch_deactivate").onchange = function () {
    if (!naiveHA_temp_control_fetching && this.checked) {
        naiveHA_temp_control_fetching = true
        naiveHA_temp_control_fetch("set_value", "On", naiveHA_temp_control_heater_status, naiveHA_temp_control_fan_status, 
            naiveHA_temp_control_target_temp, naiveHA_temp_control_room_temp, naiveHA_temp_control_control_band)
    }
}
function naiveHA_temp_control_set_fan_control() {
    if (!naiveHA_temp_control_fetching){
        naiveHA_temp_control_fetching = true
        if (naiveHA_temp_control_fan_status == "Off"){
            new_status = "On"
        } else {
            new_status = "Off"
        }
        naiveHA_temp_control_fetch("set_value", naiveHA_temp_control_status, naiveHA_temp_control_heater_status, new_status, 
            naiveHA_temp_control_target_temp, naiveHA_temp_control_room_temp, naiveHA_temp_control_control_band)
    }
}
function naiveHA_temp_control_set_temperature_target(temperature_target){
    if (!naiveHA_temp_control_fetching){
        naiveHA_temp_control_fetching = true
        naiveHA_temp_control_fetch("set_value", naiveHA_temp_control_status, naiveHA_temp_control_heater_status, naiveHA_temp_control_fan_status, 
            temperature_target, naiveHA_temp_control_room_temp, naiveHA_temp_control_control_band)
    }
}
function naiveHA_temp_control_set_control_band(control_band){
    if (!naiveHA_temp_control_fetching){
        naiveHA_temp_control_fetching = true
        naiveHA_temp_control_fetch("set_value", naiveHA_temp_control_status, naiveHA_temp_control_heater_status, naiveHA_temp_control_fan_status, 
                naiveHA_temp_control_target_temp, naiveHA_temp_control_room_temp, control_band)
    }
}
async function naiveHA_temp_control_fetch(command, status, heater_status, fan_status, target_temp, room_temp, control_band) {
    let controller = new AbortController();
    setTimeout(() => controller.abort(), 60000);
    try {
        for (i = 0; i < document.getElementsByClassName("naiveHA_temp_control_info_panel_value").length; i++) {
            document.getElementsByClassName("naiveHA_temp_control_info_panel_value")[i].style.color = "gray"
        }
        for (i = 0; i < document.getElementsByClassName("naiveHA_temp_control_switch__label").length; i++) {
            document.getElementsByClassName("naiveHA_temp_control_switch__label")[i].style.color = "gray"
        }
        for (let i = 15; i < 31; i++) {
            document.getElementById("naiveHA_temp_control_temperature_target_option_" + i).style.color = "gray"
        }
        for (let i = 2; i < 5; i++) {
            document.getElementById("naiveHA_temp_control_band_" + i).style.color = "gray"
        }
        if (command == "set_value") {
            attributes = '"{""Controller"":""' + status + '"",""Heater"":""' + heater_status + '"",""Fan"":""' + fan_status + 
            '"",""Target_temp"":""' + target_temp + '"",""Room_temp"":""' + naiveHA_temp_control_string_zero(room_temp) + '"",""Control_band"":""' + control_band + '""}"'
        } else {
            attributes = '"[""Controller"",""Heater"",""Fan"",""Target_temp"",""Room_temp"",""Control_band""]"'
        }
        await fetch('?{"command":"' + command + '","endpoint_id":"<<ENDPOINT_ID>>","attributes":' + attributes + '}', { signal: controller.signal }).then(response => response.json()).then(response => {
            naiveHA_temp_control_status = response["attributes"]["Controller"]
            naiveHA_temp_control_heater_status = response["attributes"]["Heater"]
            naiveHA_temp_control_fan_status = response["attributes"]["Fan"]
            naiveHA_temp_control_target_temp = response["attributes"]["Target_temp"]
            naiveHA_temp_control_room_temp = response["attributes"]["Room_temp"]
            naiveHA_temp_control_control_band = response["attributes"]["Control_band"]
            naiveHA_temp_control_graphics_update(naiveHA_temp_control_status, naiveHA_temp_control_heater_status, 
                naiveHA_temp_control_fan_status, naiveHA_temp_control_string_zero(naiveHA_temp_control_target_temp), 
                naiveHA_temp_control_string_zero(naiveHA_temp_control_room_temp), naiveHA_temp_control_control_band)
            naiveHA_temp_control_fetching = false
            return true
        })
    } catch (err) {
        naiveHA_temp_control_graphics_update(status, heater_status, fan_status, target_temp, room_temp, control_band)
        naiveHA_temp_control_fetching = false
    }
    return false
}
function naiveHA_temp_control_graphics_update(status, heater_status, fan_status, target_temp, room_temp, control_band) {
    document.getElementById("naiveHA_temp_control_heater_status").innerHTML = heater_status
    document.getElementById("naiveHA_temp_control_fan_status").innerHTML = fan_status
    document.getElementById("naiveHA_temp_control_target_temp").innerHTML = target_temp
    document.getElementById("naiveHA_temp_control_room_temp").innerHTML = room_temp
    for (i = 0; i < document.getElementsByClassName("naiveHA_temp_control_info_panel_value").length; i++) {
        document.getElementsByClassName("naiveHA_temp_control_info_panel_value")[i].style.color = ""
    }
    for (i = 0; i < document.getElementsByClassName("naiveHA_temp_control_switch__label").length; i++) {
        document.getElementsByClassName("naiveHA_temp_control_switch__label")[i].style.color = ""
    }
    if (status == "Off") {
        document.getElementById("naiveHA_temp_control_switch_activate").checked = true
    } else {
        document.getElementById("naiveHA_temp_control_switch_deactivate").checked = true
    }
    for (let i = 15; i < 31; i++) {
        if (i != parseInt(target_temp)) {
            document.getElementById("naiveHA_temp_control_temperature_target_option_" + i).classList.remove("naiveHA_temp_control_select_selected")
        } else {
            document.getElementById("naiveHA_temp_control_temperature_target_option_" + i).classList.add("naiveHA_temp_control_select_selected")
        }
        document.getElementById("naiveHA_temp_control_temperature_target_option_" + i).style.color = ""
    }
    for (let i = 2; i < 5; i++) {
        if (i != parseInt(2*parseFloat(control_band))) {
            document.getElementById("naiveHA_temp_control_band_" + i).classList.remove("naiveHA_temp_control_select_selected")
        } else {
            document.getElementById("naiveHA_temp_control_band_" + i).classList.add("naiveHA_temp_control_select_selected")
        }
        document.getElementById("naiveHA_temp_control_band_" + i).style.color = ""
    }
    var naiveHA_temp_control_last_refresh_id = document.getElementById("naiveHA_temp_control_last_refresh")
    const currentDate = new Date()
    naiveHA_temp_control_last_refresh_id.innerHTML = "Last refresh: " + currentDate.getFullYear() + "-" + 
    naiveHA_temp_control_addZero(currentDate.getMonth() + 1) + "-" + naiveHA_temp_control_addZero(currentDate.getDay()) + " " + 
    naiveHA_temp_control_addZero(currentDate.getHours()) + ":" + naiveHA_temp_control_addZero(currentDate.getMinutes()) + ":" + 
    naiveHA_temp_control_addZero(currentDate.getSeconds()) + "; Tap to refresh again"
}
window.addEventListener("DOMContentLoaded", naiveHA_temp_control_graphics_update(naiveHA_temp_control_status, naiveHA_temp_control_heater_status,
    naiveHA_temp_control_fan_status, naiveHA_temp_control_string_zero(naiveHA_temp_control_target_temp), 
    naiveHA_temp_control_string_zero(naiveHA_temp_control_room_temp), naiveHA_temp_control_control_band), false)
