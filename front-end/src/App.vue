<template>
  <main class="pixel-battle">
    <template v-if="!isLoading">
      <h1>Pixel Battle</h1>

      <div class="controlls">
        <div
          class="current-color"
          @click="toggleSelectionMenu"
        >
          <p>Current color:</p>
          <div
            class="current-color__marker"
            :style="{backgroundColor: `rgb(${red}, ${green}, ${blue})`}"  
          />
        </div>

        <div class="current-color">
          <p>Pixel size:</p>
          <label class="pixel-size">
            <input type="range" min="4" step="1" max="50" v-model="pixelSize">
            {{ pixelSize }}
          </label>
        </div>

        <div class="current-color">
          <label class="border-toggle">
            Borders:
            <input type="checkbox" v-model="borderVisible">
          </label>
        </div>
      </div>

      <div class="overlay"
        v-if="selectionMode"
      >
        <div class="color-selection-wrapper">
          <div class="color-selection-wrapper__result" :style="{backgroundColor: `rgb(${red}, ${green}, ${blue})`}" />

          <label>
            Red: {{ red }}
            <input type="range" min="0" max="255" step="1" v-model="red">
          </label>
          
          <label>
            Green: {{ green }}
            <input type="range" min="0" max="255" step="1" v-model="green">
          </label>

          <label>
            Blue: {{ blue }}
            <input type="range" min="0" max="255" step="1" v-model="blue">
          </label>

          <button
            class="color-selection-wrapper__button"
            @click="toggleSelectionMenu"  
          >+</button>
        </div>

      </div>

      <div class="picture">
        <div
          class="picture__row"
          v-for="(row, rowIndex) of pixels"
          :key="'row_' + rowIndex + 1"
        >
          <div
            class="picture__pixel"
            :style="{
                backgroundColor: color,
                height: `${pixelSize}px`,
                width: `${pixelSize}px`,
                borderColor: borderVisible ? 'black' : color
              }"
            v-for="(color, columnIndex) of row"
            :key="'column_' + columnIndex + 1"
            @click="handlePixelClick(rowIndex, columnIndex)"
          />
        </div>
      </div>
    </template>
  </main>
</template>

<script>
import axios from 'axios';

const SERVER_ADDRES = process.env.API_ADDRESS || '127.0.0.1'
const PORT = process.env.API_PORT || 5000

const ADDRESS = `http://${SERVER_ADDRES}:${PORT}`
const SOCKET = `ws://${SERVER_ADDRES}:${PORT}`

export default {
  name: 'App',
  data () {
    return {
      pixelSize: 4,
      borderVisible: true,
      selectionMode: false,
      red: 106,
      green: 144,
      blue: 195,
      selectedColor: '#000000',
      pixels: [],
      canIClick: true,
      isLoading: true,
    }
  },
  methods: {
    handleColorChange(event) {
      console.log(event.target.value)
    },
    async handlePixelClick (indexI, indexJ) {
      if (!this.canIClick) return
      
      const r = Number(this.red).toString(16)
      const g = Number(this.green).toString(16)
      const b = Number(this.blue).toString(16)

      const newColor = `#${r.length === 2 ? r : '0' + r}${g.length === 2 ? g : '0' + g}${b.length === 2 ? b : '0' + b}`
    
      try {
        const response = await axios.post(`${ADDRESS}/pixel`, {
          x: indexI,
          y: indexJ,
          color: newColor
        })


        // this.canIClick = false

        // setTimeout(() => {
        //   this.canIClick = true
        // }, 20000)
      } catch (error) {

      }
    },
    toggleSelectionMenu () {
      this.selectionMode = !this.selectionMode
    },
    async initMatrix () {
      
      try {
        const response = await axios.get(`${ADDRESS}/matrix`)
        this.pixels = response.data
        this.isLoading = false
      } catch (error) {
        console.error(error)
      }
    }
  },
  mounted () {
    this.initMatrix()

    const socket = new WebSocket(`${SOCKET}/sock`);
      socket.addEventListener('message', (event) => {
        this.pixels = JSON.parse(event.data)
      })
  }
}
</script>

<style lang="scss">
* {
  padding: 0;
  margin: 0;
}

body {
  min-height: 100vh;
  padding: 0 15px 15px;
  width: fit-content;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;

  label {
    display: flex;
    flex-direction: column;
    margin-top: 12px;
  }
}

.pixel-battle {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;

  h1 {
    margin: 16px 0;
  }
}

.color-selection-wrapper {
  position: relative;
  background-color: white;
  border-radius: 8px;
  padding: 50px;

  &__result {
    height: 50px;
    width: 50px;
    border-radius: 4px;
    border: 1px solid black;
  }

  &__button {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    font-size: 36px;
    transform: rotate(45deg);
    cursor: pointer;
    border: 0;
    background: transparent;
  }
}

.pixel-size {
  margin-left: 4px;
}

.picture {
  border: 0.5px solid black;
  display: flex;
  flex-direction: column;
  width: fit-content;

  &__row {
    display: flex;
  }

  &__pixel {
    min-height: 10px;
    min-width: 10px;
    border: 1px solid black;

    &:hover {
      position: relative;
      transform: scale(1.5);
      border-color: black !important;
    }
  }
}

@keyframes kekpek {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.current-color {
  margin-bottom: 15px;
  align-self: flex-start;
  cursor: pointer;
  font-size: 22px;
  display: flex;
  align-items: center;

  &__marker {
    margin-left: 4px;
    height: 20px;
    width: 20px;
    border: 1px solid black;
    border-radius: 4px;
  }
}

.loader {
  justify-self: center;
  align-self: center;
}

.border-toggle {
  display: flex;
  align-items: center;

  input {
    margin-left: 4px;
    height: 20px;
    width: 20px;
  }
}
</style>
