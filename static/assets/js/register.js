function validateForm() {
    let phone = document.getElementById("phone").value;
    if (!phone.match(/^\+?\d{0,3}\s?-?\d{6,10}$/)) {
        alert("Please enter a valid phone number with country code.");
        return false;
    }
    return true;
}