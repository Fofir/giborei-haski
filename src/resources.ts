import { TiledResource } from '@excaliburjs/plugin-tiled'
import * as ex from 'excalibur'
import { GiboreiLoader } from './ui/loader'

const BASE_URL = process.env.NODE_ENV === 'production' ? '/giborei-haski' : '';

export const Resources = {
  img: {
    player: new ex.ImageSource(BASE_URL + '/res/images/Player.png'),
    dolomitiSky: new ex.ImageSource(BASE_URL + '/res/images/Dolomiti_Sky.png'),
    dolomitiMountains: new ex.ImageSource(BASE_URL + '/res/images/Dolomiti_Mountains.png'),
    dolomitiValley: new ex.ImageSource(BASE_URL + '/res/images/Dolomiti_Valley.png'),
    spiderGreen: new ex.ImageSource(BASE_URL +'/res/images/Spider_1.png'),
    spiderGray: new ex.ImageSource(BASE_URL +'/res/images/Spider_2.png'),
    birdPurple: new ex.ImageSource(BASE_URL +'/res/images/Bird_1.png'),
    birdOrange: new ex.ImageSource(BASE_URL +'/res/images/Bird_2.png'),
    platform: new ex.ImageSource(BASE_URL +'/res/images/Platform.png'),
    bouncepadGreen: new ex.ImageSource(BASE_URL +'/res/images/Bouncepad_Green.png'),
    bouncepadRed: new ex.ImageSource(BASE_URL +'/res/images/Bouncepad_Red.png'),
    bouncepadWood: new ex.ImageSource(BASE_URL +'/res/images/Bouncepad_Wood.png'),
    axe: new ex.ImageSource(BASE_URL +'/res/images/Axe_Trap.png'),
    circularSaw: new ex.ImageSource(BASE_URL +'/res/images/Circular_Saw.png'),
    smokePuff: new ex.ImageSource(BASE_URL +'/res/images/Smoke_Puff.png'),
    smokeLand: new ex.ImageSource(BASE_URL +'/res/images/Smoke_Land.png'),
    coin: new ex.ImageSource(BASE_URL +'/res/images/Coin.png'),
    bolognese: new ex.ImageSource(BASE_URL + '/res/images/Bolognese.png'),
    title: new ex.ImageSource(BASE_URL + '/res/images/Title.png'),
    titlePress: new ex.ImageSource(BASE_URL + '/res/images/Title_Press.png'),
    coinsUi: new ex.ImageSource(BASE_URL +'/res/images/Coins_Ui.png'),
  },

  fonts: {
    round: new ex.FontSource(BASE_URL + '/res/fonts/Round9x13.ttf', 'Round9x13', {
      filtering: ex.ImageFiltering.Pixel,
      quality: 4,
    }),
  },
  music: {
    stage1: new ex.Sound(BASE_URL +'/res/music/giborei-haski-instrumental.mp3'),
    stage2: new ex.Sound(BASE_URL +'/res/music/stage2.mp3'),
  },
  sfx: {
    jump: new ex.Sound(BASE_URL +'/res/sfx/jump.wav'),
    jumpSpring: new ex.Sound(BASE_URL +'/res/sfx/jump-spring.wav'),
    land: new ex.Sound(BASE_URL +'/res/sfx/land.wav'),
    turnAround: new ex.Sound(BASE_URL +'/res/sfx/turn-around.wav'),
    stomp: new ex.Sound(BASE_URL +'/res/sfx/stomp.wav'),
    damage: new ex.Sound(BASE_URL +'/res/sfx/damage.wav'),
    collectCoin: new ex.Sound(BASE_URL +'/res/sfx/coin.wav'),
    powerup: new ex.Sound(BASE_URL + '/res/sfx/powerup.wav'),
    playerDie: new ex.Sound(BASE_URL + '/res/sfx/player-die.wav'),
  },
  tiled: {
    level1: new TiledResource(BASE_URL + '/res/tilemaps/level1.tmx', {
      useTilemapCameraStrategy: true,
    }),
  },
} as const

export const loader = new GiboreiLoader()

for (const group of Object.values(Resources)) {
  for (const resource of Object.values(group)) {
    loader.addResource(resource)
  }
}
