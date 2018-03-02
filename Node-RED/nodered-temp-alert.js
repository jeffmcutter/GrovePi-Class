
temperature = msg.payload.data.temperature;

for (var key in msg.payload.data) {
    delete msg.payload.data[key];
}

if (temperature >= 21) {
    alert = "not-ok";
} else {
    alert = "ok";
}

msg.payload.data.type = alert;

return msg;