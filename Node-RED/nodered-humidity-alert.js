
humidity = msg.payload.data.humidity;

for (var key in msg.payload.data) {
    delete msg.payload.data[key];
}

if (humidity > 80) {
    alert = "not-ok";
} else {
    alert = "ok";
}

msg.payload.data.type = alert;

return msg;