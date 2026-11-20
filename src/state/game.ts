import { EventEmitter } from 'excalibur'

let coins = 0

/**
 * A general manager for game state
 */
export abstract class GameManager {
  static events = new EventEmitter<GameManagerEvents>()

  /**
   * The amount of coins collected
   */
  static get coins() {
    return coins
  }

  static set coins(value: number) {
    if (value < 0) {
      value = 0
    }
    coins = value
    GameManager.events.emit('coinchange', { coins })
  }
}

export interface GameManagerEvents {
  coinchange: { coins: number }
  playerdied: void
}
