<template>
  <v-app class="pixel-battle">
    <div class="d-flex justify-center pa-5">
      <v-img contain max-height="50" max-width="656" src="./assets/title.png"></v-img>
    </div>
    <div class="d-flex justify-center pa-5">
      <Compact v-model="colors" />
    </div>
    <div class="d-flex justify-center">
      <canvas id="canvas" width="1500" height="1200"></canvas>
    </div>
    <v-dialog v-model="dialog">
      <v-card color="#5485ae" theme="dark" class="tonal pa-md-6 mx-lg-auto">
        <v-card-title>
          Закрашивать пикслель можно раз в 5 с
        </v-card-title>
      </v-card>
    </v-dialog>
    <v-footer padless>
      <v-col class="text-center" cols="12">
        {{ new Date().getFullYear() }} — <strong>Developed on VSFI</strong>
      </v-col>
    </v-footer>
  </v-app>
</template>

<script>
import axios from 'axios';
import { Compact } from '@ckpack/vue-color';


const SERVER_ADDRES = document.location.host;
//const SERVER_ADDRES = "localhost";
const PORT = process.env.API_PORT || 80

const ADDRESS = `http://${SERVER_ADDRES}/api/v1`
const SOCKET = `ws://${SERVER_ADDRES}/api/v1`

export default {
  name: 'App',
  components: {
    Compact,
  },
  setup() {
    return {
      colors: { hex: '#009CE0' }
    }
  },
  data() {
    return {
      dialog: false,
      block: false,
      seconds: 10,
      pixelSize: 15,
      borderVisible: true,
      selectionMode: false,
      elements: [],
      pixels: [],
      canIClick: true,
      isLoading: true,
    }
  },
  methods: {
    toggleSelectionMenu() {
      this.selectionMode = !this.selectionMode
    },
    async getData() {
      return await axios({
        url: `${ADDRESS}/matrix`,
        method: 'get',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then(res => { this.pixels = res.data })
        .catch(err => console.error(err))
    },
    async sendPixel(x, y) {
      if (this.dialog == false) {
        return await axios({
          url: `${ADDRESS}/pixel`,
          method: 'post',
          headers: {
            'Content-Type': 'application/json',
          },
          data: {
            x: x,
            y: y,
            color: this.colors.hex
          }
        }).then(res => res.data)
          .catch(err => console.error(err))
      }
    },
    blockMatrix() {
      this.block = true
      setTimeout(() => {
        this.dialog = false
        this.block = false
      }, 5 * 1000)
    },
    showDialog() {
      this.dialog = true
    },
    draw() {
      var elem = document.getElementById('canvas'),
        context = elem.getContext('2d');

      this.elements = []
      for (var i = 0; i < this.pixels.length; i++) {
        var pixel = this.pixels[i];
        for (var j = 0; j < pixel.length; j++) {
          this.elements.push({
            color: this.pixels[i][j],
            width: this.pixelSize,
            height: this.pixelSize,
            top: i * this.pixelSize,
            left: j * this.pixelSize
          })
        }
      }
      this.elements.forEach(function (element) {
        context.fillStyle = element.color;
        context.fillRect(element.left, element.top, element.width, element.height);
        context.strokeStyle = "#FFFFFF";
        context.lineWidth = 2;
        context.strokeRect(element.left, element.top, element.width, element.height);
      })
    },
    render_matrix() {
      // Render elements.
      var elem = document.getElementById('canvas'),
        context = elem.getContext('2d');
      this.elements.forEach(function (element) {
        context.fillStyle = element.color;
        context.fillRect(element.left, element.top, element.width, element.height);
        context.strokeStyle = "#FFFFFF";
        context.lineWidth = 2;
        context.strokeRect(element.left, element.top, element.width, element.height);
      })
    },
    listener() {
      var elem = document.getElementById('canvas'),
        elemLeft = elem.offsetLeft + elem.clientLeft,
        elemTop = elem.offsetTop + elem.clientTop
      // Add event listener for `click` events.
      var vm = this
      elem.addEventListener('click', function (event) {
        var x = event.pageX - elemLeft,
          y = event.pageY - elemTop;
        var pixel_x = Math.floor(x / vm.pixelSize),
          pixel_y = Math.floor(y / vm.pixelSize)
        if (vm.block == false) {
          vm.pixels[pixel_y][pixel_x] = vm.colors.hex
          vm.draw()
          vm.sendPixel(pixel_y, pixel_x)
          vm.blockMatrix()
          vm.block == true
        } else {
          vm.showDialog()
        }
      }, false);
    }
  },

  async mounted() {
    await this.getData()
    this.draw()
    this.listener()
    const socket = new WebSocket(`${SOCKET}/sock`);
    socket.addEventListener('message', (event) => {
      this.pixels = JSON.parse(event.data)
      this.draw()
    })
  }
}
</script>
<style scoped>
</style>