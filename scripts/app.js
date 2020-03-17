window.onload = function () {
    var app = new Vue({
        el: '#app',
        data: {
            leftPitch: null,
            rightPitch: null,
            message: 'Hello Vue!',
            files: [
                "../firmware/TCO1_6_60Hz_Internal.d3",
                "../firmware/TCO2_0_60Hz_Internal.d3",
                "../firmware/TCO2_5_60Hz_Internal.d3",
                "../firmware/TCO4_0_60Hz_Internal.d3"
            ],
            fw: null
        },
        mounted() {
            this.getFirmwareFiles()
        },
        methods: {
            readLocalFile: async function(url) {
                return new Promise(function(resolve, reject) {
                    var xhr = new XMLHttpRequest;
                    xhr.onload = function() {
                        resolve(new Response(xhr.responseText, {status: xhr.status}))
                    };
                    xhr.onerror = function() {
                        reject(new TypeError('Local request failed'))
                    };
                    xhr.open('GET', url);
                    xhr.send(null)
                })
            },


            getFirmwareFiles: function() {
                firmware = this.files[0];
                url = 'file:///' + firmware;
                this.readLocalFile(url)
                    .then((data) => {
                        console.log(data); // JSON data parsed by `response.json()` call
                    });




            },
            updateFirmware: function () {
                let self = this;
                mac = "00:18:B7:89:45:40";
                let data = new FormData();
                data.append('file', this.files);
                data.append('ids', mac);
                // this.set('isFirmwareUpdating', true);

                axios.post('http://10.0.0.3/api/devices?command=update-firmware', data)
                    .then(function (response) {
                        console.log(response)

                    }).catch(function (error) {
                    console.log(error)

                })
            },
        },
    });
};

