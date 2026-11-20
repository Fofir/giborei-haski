import * as ex from 'excalibur'
import { CollectableComponent } from '../../components/behaviours/collectable'
import { Resources } from '../../resources'
import { CollisionGroup } from '../../physics/collision'
import Player from '../player'

/**
 * Power-up: a plate of spaghetti Bolognese (works like Mario's super mushroom).
 * Sits still until it scrolls on screen, then slides along the ground, falls off ledges
 * and turns around at walls. Makes the player big.
 */
export class BologneseItem extends ex.Actor {
  SPEED = 45

  direction: 1 | -1
  isMoving = false

  constructor(args: ex.ActorArgs & { direction?: 'left' | 'right' }) {
    super({
      anchor: ex.vec(0.5, 1),
      collisionType: ex.CollisionType.Active,
      collisionGroup: CollisionGroup.PhysicalItem,
      collider: ex.Shape.Box(12, 12, ex.vec(0.5, 1)),
      ...args,
    })

    this.direction = args.direction === 'left' ? -1 : 1
    this.addComponent(new CollectableComponent())
    this.graphics.use(Resources.img.bolognese.toSprite())
  }

  get collectable() {
    return this.get(CollectableComponent)
  }

  onInitialize(): void {
    this.on('postcollision', (ev) => {
      const isWall = ev.side === ex.Side.Left || ev.side === ex.Side.Right
      if (isWall && !(ev.other instanceof Player)) {
        this.direction = ev.side === ex.Side.Left ? 1 : -1
      }
    })
  }

  onPreUpdate(): void {
    // start sliding once the camera can see us
    if (!this.isMoving && this.scene!.camera.viewport.overlaps(this.collider.bounds)) {
      this.isMoving = true
    }

    this.vel.x = this.isMoving ? this.SPEED * this.direction : 0
  }

  onPreCollisionResolve(
    self: ex.Collider,
    other: ex.Collider,
    side: ex.Side,
    contact: ex.CollisionContact
  ): void {
    if (other.owner instanceof Player) {
      contact.cancel()
      this.collect(other.owner)
    }
  }

  collect(player: Player) {
    if (this.collectable.isCollected || player.isDead) return

    this.collectable.isCollected = true
    player.grow()
    this.kill()
  }
}
