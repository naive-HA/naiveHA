var naiveHA_arlec_state = "<<POWER>>"
var naiveHA_arlec_fetching = false
document.getElementById("yes").onchange = function () {
    if (!naiveHA_arlec_fetching && this.checked) {
        naiveHA_arlec_fetching = true
        for (i = 0; i < document.getElementsByClassName("naiveHA_arlec_switch__label").length; i++) {
            document.getElementsByClassName("naiveHA_arlec_switch__label")[i].style.color = "gray"
        }
        naiveHA_arlec_fetch("On")
    }
}
document.getElementById("no").onchange = function () {
    if (!naiveHA_arlec_fetching && this.checked) {
        naiveHA_arlec_fetching = true
        for (i = 0; i < document.getElementsByClassName("naiveHA_arlec_switch__label").length; i++) {
            document.getElementsByClassName("naiveHA_arlec_switch__label")[i].style.color = "gray"
        }
        naiveHA_arlec_fetch("Off")
    }
}
async function naiveHA_arlec_fetch(new_state) {
    let controller = new AbortController();
    setTimeout(() => controller.abort(), 60000);
    try {
        await fetch('?{"command":"set_value","endpoint_id":"<<ENDPOINT_ID>>","attributes":"{""Power"":""' + new_state + '""}"}', { signal: controller.signal }).then(response => response.json()).then(response => {
            naiveHA_arlec_state = response["attributes"]["Power"]
            naiveHA_arlec_refresh(naiveHA_arlec_state)
            naiveHA_arlec_fetching = false
            return true
        })
    } catch (err) {
        naiveHA_arlec_refresh(naiveHA_arlec_state)
        naiveHA_arlec_fetching = false
        return false
    }
    return false
}
function naiveHA_arlec_refresh(power_arlec_selected_value) {
    var power_arlec_On = document.getElementById("yes")
    var power_arlec_Off = document.getElementById("no")
    for (i = 0; i < document.getElementsByClassName("naiveHA_arlec_switch__label").length; i++) {
        document.getElementsByClassName("naiveHA_arlec_switch__label")[i].style.color = "white"
    }
    if (power_arlec_selected_value == "On") {
        power_arlec_On.checked = true
    } else {
        power_arlec_Off.checked = true
    }
}
window.addEventListener("DOMContentLoaded", naiveHA_arlec_refresh(naiveHA_arlec_state), false)
