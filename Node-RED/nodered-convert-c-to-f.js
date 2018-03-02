// Convert the payload as follows:
//   1. Delete all non temperature data points.
//   2. Convert temp from C to F.
//
// Sample payload
// {"timestamp": 1519609945872, "data": {"range": 511, "degrees": 222.0, "temperature": 19.0, "humidity": 47.0}}

temperature = msg.payload.data.temperature

for (var key in msg.payload.data) {
    //if (key !== "temperature")
    delete msg.payload.data[key];
}

msg.payload.data.temperature_c = temperature.toFixed(1);
msg.payload.data.temperature_f = (temperature * 9 / 5 + 32).toFixed(1);
return msg;