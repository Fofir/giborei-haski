import * as ex from 'excalibur'

const BASE_URL = process.env.NODE_ENV === 'production' ? '/giborei-haski' : ''

const ART_WIDTH = 398
const ART_HEIGHT = 224
const BAR_WIDTH = 160
const BAR_HEIGHT = 6
const BAR_Y = 196

/**
 * Giborei Ha'Ski loading screen: the title art with Dudu skiing along a progress bar,
 * then "CLICK TO START" (the click also unlocks browser audio so the title music can play).
 */
export class GiboreiLoader extends ex.DefaultLoader {
  // the loader's own art is fetched before everything else so it can be drawn while loading
  private art = {
    title: new ex.ImageSource(BASE_URL + '/res/images/Title.png'),
    player: new ex.ImageSource(BASE_URL + '/res/images/Player.png'),
    loading: new ex.ImageSource(BASE_URL + '/res/images/Loader_Loading.png'),
    click: new ex.ImageSource(BASE_URL + '/res/images/Loader_Click.png'),
  }
  private artLoaded = false
  private shownProgress = 0
  private elapsed = 0

  constructor() {
    super()
    this.canvas.filtering = ex.ImageFiltering.Pixel
    this.canvas.smoothing = false
  }

  async onBeforeLoad() {
    await Promise.all(Object.values(this.art).map((image) => image.load()))
    this.artLoaded = true
  }

  async onUserAction() {
    await new Promise<void>((resolve) => {
      const start = () => {
        window.removeEventListener('pointerdown', start)
        window.removeEventListener('keydown', start)
        resolve()
      }
      window.addEventListener('pointerdown', start)
      window.addEventListener('keydown', start)
    })
  }

  async onAfterLoad() {
    // no extra delay: the title screen fades straight in
  }

  onUpdate(engine: ex.Engine, elapsedMs: number): void {
    super.onUpdate(engine, elapsedMs)
    this.elapsed += elapsedMs
    // ease the bar towards the real progress so Dudu glides instead of jumping
    this.shownProgress += (this.progress - this.shownProgress) * Math.min(1, elapsedMs / 120)
    this.canvas.flagDirty()
  }

  onDraw(ctx: CanvasRenderingContext2D): void {
    const { width, height } = this.engine.screen.resolution
    ctx.imageSmoothingEnabled = false
    ctx.fillStyle = '#2f5fae'
    ctx.fillRect(0, 0, width, height)
    if (!this.artLoaded) return

    // same cover-scaling as the title scene so the hand-off is seamless
    const scale = Math.max(width / ART_WIDTH, height / ART_HEIGHT)
    const ox = (width - ART_WIDTH * scale) / 2
    const oy = (height - ART_HEIGHT * scale) / 2
    const at = (x: number, y: number) => [ox + x * scale, oy + y * scale] as const

    ctx.drawImage(this.art.title.image, ox, oy, ART_WIDTH * scale, ART_HEIGHT * scale)

    if (this.isLoaded()) {
      // blink "CLICK TO START" where "PRESS ENTER" will appear
      if (Math.floor(this.elapsed / 500) % 2 === 0) {
        const img = this.art.click.image
        const [x, y] = at((ART_WIDTH - img.width) / 2, 188)
        ctx.drawImage(img, x, y, img.width * scale, img.height * scale)
      }
      return
    }

    const barX = (ART_WIDTH - BAR_WIDTH) / 2
    const fill = Math.round(BAR_WIDTH * this.shownProgress)

    const rect = (x: number, y: number, w: number, h: number, color: string) => {
      const [sx, sy] = at(x, y)
      ctx.fillStyle = color
      ctx.fillRect(sx, sy, w * scale, h * scale)
    }
    rect(barX - 2, BAR_Y - 2, BAR_WIDTH + 4, BAR_HEIGHT + 4, '#1a1020') // outline
    rect(barX - 1, BAR_Y - 1, BAR_WIDTH + 2, BAR_HEIGHT + 2, '#ffffff') // snow frame
    rect(barX, BAR_Y, BAR_WIDTH, BAR_HEIGHT, '#8eaacb') // empty track
    rect(barX, BAR_Y, fill, BAR_HEIGHT, '#d8262a') // red ski-run fill
    rect(barX, BAR_Y, fill, 2, '#ff6a5a')

    // Dudu skiing along the bar (sprint frames 8-11 of the player sheet, feet at y=31 of a 48px cell)
    const frame = 8 + (Math.floor(this.elapsed / 90) % 4)
    const [dx, dy] = at(barX + fill - 24, BAR_Y - 2 - 31)
    ctx.drawImage(
      this.art.player.image,
      (frame % 4) * 48,
      Math.floor(frame / 4) * 48,
      48,
      48,
      dx,
      dy,
      48 * scale,
      48 * scale
    )

    const label = this.art.loading.image
    const [lx, ly] = at((ART_WIDTH - label.width) / 2, BAR_Y + BAR_HEIGHT + 3)
    ctx.drawImage(label, lx, ly, label.width * scale, label.height * scale)
  }
}
