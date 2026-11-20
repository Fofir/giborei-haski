import * as ex from 'excalibur'
import { Resources } from '../resources'
import { AudioManager } from '../state/audio'

const ART_WIDTH = 398
const ART_HEIGHT = 224

/**
 * Sonic-style title screen. Press Enter / Space / A / S, click, or press a gamepad button to start.
 */
export default class Title extends ex.Scene {
  private started = false
  private art!: ex.ScreenElement
  private press!: ex.ScreenElement
  private elapsed = 0
  private activeFor = 0

  onInitialize(engine: ex.Engine): void {
    this.backgroundColor = ex.Color.fromHex('#2f5fae')

    this.art = new ex.ScreenElement({ anchor: ex.vec(0, 0) })
    this.art.graphics.use(Resources.img.title.toSprite())
    this.add(this.art)

    this.press = new ex.ScreenElement({ anchor: ex.vec(0, 0) })
    this.press.graphics.use(Resources.img.titlePress.toSprite())
    this.add(this.press)
    this.layout(engine)

    this.input.keyboard.on('press', (ev) => {
      const startKeys = [ex.Keys.Enter, ex.Keys.Space, ex.Keys.A, ex.Keys.S]
      if (startKeys.includes(ev.key)) this.start()
    })
    this.input.pointers.primary.on('down', () => this.start())
    this.input.gamepads.on('button', () => this.start())
  }

  onActivate(): void {
    this.started = false
    this.activeFor = 0
    AudioManager.playSong(Resources.music.stage1)
  }

  /**
   * Scales the art to cover the whole screen (the draw size depends on the window).
   */
  layout(engine: ex.Engine) {
    const scale = Math.max(engine.drawWidth / ART_WIDTH, engine.drawHeight / ART_HEIGHT)
    const offset = ex.vec(
      (engine.drawWidth - ART_WIDTH * scale) / 2,
      (engine.drawHeight - ART_HEIGHT * scale) / 2
    )
    const pressWidth = Resources.img.titlePress.width

    this.art.pos = offset
    this.art.scale = ex.vec(scale, scale)
    this.press.pos = offset.add(ex.vec(((ART_WIDTH - pressWidth) / 2) * scale, 188 * scale))
    this.press.scale = ex.vec(scale, scale)
  }

  onPreUpdate(engine: ex.Engine, delta: number): void {
    this.layout(engine)

    // blink "PRESS ENTER" (faster once the game is starting)
    this.elapsed += delta
    this.activeFor += delta
    const rate = this.started ? 80 : 500
    this.press.graphics.visible = Math.floor(this.elapsed / rate) % 2 === 0
  }

  start() {
    // ignore the click/key that dismissed the loading screen
    if (this.started || this.activeFor < 400) return
    this.started = true

    AudioManager.playSfx(Resources.sfx.powerup, { force: true })
    ex.coroutine(
      this.engine,
      function* (this: Title): ReturnType<ex.CoroutineGenerator> {
        yield 600
        this.engine.goToScene('level1')
      }.bind(this)
    )
  }
}
