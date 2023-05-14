var naiveHA_spector_power = "<<POWER>>"
var naiveHA_spector_heat = "<<HEAT_LEVEL>>"
var naiveHA_spector_fan = "<<FAN>>"
var naiveHA_spector_temp = "<<TEMP>>"
var naiveHA_spector_fetching = false

async function naiveHA_spector_set_power(power) {
    if (!naiveHA_spector_fetching) {
        naiveHA_spector_fetching = true
        await naiveHA_spector_fetch("set_value", power, naiveHA_spector_heat, naiveHA_spector_fan, naiveHA_spector_temp)
    }
}
async function naiveHA_spector_set_heat(heat) {
    if (!naiveHA_spector_fetching) {
        naiveHA_spector_fetching = true
        await naiveHA_spector_fetch("set_value", naiveHA_spector_power, heat, naiveHA_spector_fan, naiveHA_spector_temp)
    }
}
async function naiveHA_spector_set_fan(fan) {
    if (!naiveHA_spector_fetching) {
        naiveHA_spector_fetching = true
        await naiveHA_spector_fetch("set_value", naiveHA_spector_power, naiveHA_spector_heat, fan, naiveHA_spector_temp)
    }
}
async function naiveHA_spector_set_temp(temp) {
    if (!naiveHA_spector_fetching) {
        naiveHA_spector_fetching = true
        await naiveHA_spector_fetch("set_value", naiveHA_spector_power, naiveHA_spector_heat, naiveHA_spector_fan, temp)
    }
}
async function naiveHA_spector_fetch(command, p, h, f, t) {
    let controller = new AbortController();
    setTimeout(() => controller.abort(), 60000);
    try {
        for (i = 0; i < document.getElementsByClassName("naiveHA_spector_option").length; i++) {
            document.getElementsByClassName("naiveHA_spector_option")[i].style.color = "grey"
        }
        if (command == "set_value") {
            attributes = '"{""Power"":""' + p + '"",""HeatLevel"":""' + h + '"",""Fan"":""' + f + '"",""Temp"":""' + t + '""}"'
        } else {
            attributes = '"[""Power"",""HeatLevel"",""Fan"",""Temp""]"'
        }
        await fetch('?{"command":"' + command + '","endpoint_id":"<<ENDPOINT_ID>>","attributes":' + attributes + '}', { signal: controller.signal }).then(response => response.json()).then(response => {
            naiveHA_spector_power = response["attributes"]["Power"]
            naiveHA_spector_heat = response["attributes"]["HeatLevel"]
            naiveHA_spector_fan = response["attributes"]["Fan"]
            naiveHA_spector_temp = response["attributes"]["Temp"]
            naiveHA_spector_refresh(naiveHA_spector_power, naiveHA_spector_heat, naiveHA_spector_fan, naiveHA_spector_temp)
            naiveHA_spector_fetching = false
            return true
        })
    } catch (err) {
        naiveHA_spector_refresh(naiveHA_spector_power, naiveHA_spector_heat, naiveHA_spector_fan, naiveHA_spector_temp)
        naiveHA_spector_fetching = false
        return false
    }
}
function naiveHA_spector_refresh(p, h, f, t) {
    for (i = 0; i < document.getElementsByClassName("naiveHA_spector_option").length; i++) {
        document.getElementsByClassName("naiveHA_spector_option")[i].style.color = ""
    }
    if (p == "Off") {
        document.getElementById("naiveHA_spector_temp_carousel").scrollLeft = 0
        document.getElementById("naiveHA_spector_power_option_On").classList.remove("naiveHA_spector_selected")
        document.getElementById("naiveHA_spector_power_option_Off").classList.add("naiveHA_spector_selected")
    } else {
        document.getElementById("naiveHA_spector_power_option_On").classList.add("naiveHA_spector_selected")
        document.getElementById("naiveHA_spector_power_option_Off").classList.remove("naiveHA_spector_selected")
    }
    for (let i = 1; i < 5; i++) {
        if (i != parseInt(h)) {
            document.getElementById("naiveHA_spector_heat_option_" + i).classList.remove("naiveHA_spector_selected")
        } else {
            document.getElementById("naiveHA_spector_heat_option_" + i).classList.add("naiveHA_spector_selected")
        }
    }
    if (f == "Off") {
        document.getElementById("naiveHA_spector_fan_option_Off").classList.add("naiveHA_spector_selected")
        document.getElementById("naiveHA_spector_fan_option_On").classList.remove("naiveHA_spector_selected")
    } else {
        document.getElementById("naiveHA_spector_fan_option_Off").classList.remove("naiveHA_spector_selected")
        document.getElementById("naiveHA_spector_fan_option_On").classList.add("naiveHA_spector_selected")
    }
    for (let i = 5; i < 38; i++) {
        if (i != parseInt(t)) {
            document.getElementById("naiveHA_spector_temp_option_" + i).classList.remove("naiveHA_spector_selected")
        } else {
            document.getElementById("naiveHA_spector_temp_option_" + i).classList.add("naiveHA_spector_selected")
        }
    }
}
window.addEventListener("DOMContentLoaded", naiveHA_spector_refresh(naiveHA_spector_power, naiveHA_spector_heat, naiveHA_spector_fan, naiveHA_spector_temp), false)
