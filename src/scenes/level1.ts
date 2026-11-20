import { TiledResource } from '@excaliburjs/plugin-tiled'
import { Resources } from '../resources'
import LevelScene from '../classes/level-scene'

export default class Level1 extends LevelScene {
  constructor(tilemap: TiledResource = Resources.tiled.level1) {
    super({
      tilemap,
      // Val Gardena, Dolomiti — far to near
      backgrounds: [
        { image: Resources.img.dolomitiSky, xSpeed: 0, ySpeed: 0, repeatY: false },
        { image: Resources.img.dolomitiMountains, xSpeed: 0.08, ySpeed: 0.04, repeatY: false },
        { image: Resources.img.dolomitiValley, xSpeed: 0.25, ySpeed: 0.12, repeatY: false },
      ],
      song: Resources.music.stage1,
    })
  }
}
