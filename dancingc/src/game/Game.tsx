import React, { useState } from 'react';
import { Card } from "./Card";
import { shuffle, chunk } from './Utils';
import './Game.css';

type Distribution = Array<[Card, number]>

interface Props {
    names: Array<string>,
}

interface Player {
    name: string,
    cards?: Array<Card>,
    selectedIdx?: number,
    selectedPlayer? : Player,
    conspired : boolean,
}

interface GameState {
    players: Array<Player>,
    turn: number,
    turnCounter: number,
    playedCard?: Card,
    target? : Player,
    shown? : [Array<Card>, Player],
}

const startGame = (names: string[]) => {
    const defaultConfigs = new Map<Number, Distribution>([
        [7, new Array<[Card, number]>(
            [Card.SUSPECT, 1],
            [Card.DETECTIVE, 2],
            [Card.ARIBI, 3],
            [Card.DOG, 1],
            [Card.WITNESS, 3],
            [Card.MANIPULATION, 3],
            [Card.RUMOR, 4],
            [Card.TRADE, 5],
            [Card.BOY, 1],
            [Card.CITIZEN, 2],
            [Card.CONSPIRE, 2],
            [Card.DISCOVERER, 1]
        )]
    ]);
    const state: GameState = {
        turn: -1,
        turnCounter: 0,
        players: new Array<Player>(),
    };
    const playerNumber = names.length;
    const distribution = defaultConfigs.get(playerNumber);
    if (distribution) {
        const deck: Array<Card> = shuffle(distribution.flatMap(([card, n]) => Array(n).fill(card)));
        const hands: Card[][] = chunk(deck, 4);
        state.players = names.map((name, idx) => {
            return {
                name: name,
                cards: hands[idx],
                conspired : false,
            };
        })
        state.turn = Math.floor(deck.indexOf(Card.DISCOVERER) / 4);
    }

    return state;
}

const playCard = (prevState: GameState, pIdx: number, hIdx: number) => {
    const players = prevState.players;
    const turnPlayer = players[prevState.turn];
    const selected = turnPlayer.cards?.at(hIdx);

    if (prevState.turn !== pIdx ||
        (prevState.turnCounter === 0 && selected !== Card.DISCOVERER) ||
        (prevState.turnCounter < players.length && selected === Card.DETECTIVE) ||
        (turnPlayer.cards?.length !== 1 && selected === Card.SUSPECT)
    ) {
        return prevState;
    }

    if (turnPlayer.selectedIdx !== hIdx) {
        turnPlayer.selectedIdx = hIdx;
        return {
            ...prevState,
            players
        }
    }

    const chosen = turnPlayer.cards?.splice(hIdx, 1)[0];
    turnPlayer.selectedIdx = undefined;
    return {
        ...prevState,
        players,
        turn: (prevState.turn + 1) % prevState.players.length,
        turnCounter: prevState.turnCounter + 1,
        playedCard: chosen,
    };
}

export default function Game(props: Props) {
    const [gameState, setGameState] = useState<GameState>(startGame(props.names));

    return (
        <>
            <p>出札：{gameState.playedCard?.name}</p>
            <table className='gameTable'>
                <thead>
                    <tr>
                        <th>プレイヤー</th>
                        <th colSpan={4}>手札</th>
                    </tr>
                </thead>
                <tbody>
                    {gameState.players.map((player, pIdx) => {
                        return (
                            <tr key={pIdx}>
                                <th className={gameState.turn === pIdx ? 'turnPlayer' : ''}>{player.name}</th>
                                {[0, 1, 2, 3].map(hIdx =>
                                    <td key={hIdx} className={gameState.turn === pIdx && gameState.players[gameState.turn].selectedIdx === hIdx ? 'cardSelected' : ''} onClick={() => {
                                        setGameState(playCard(gameState, pIdx, hIdx))
                                    }}>
                                        {player.cards?.at(hIdx)?.name}
                                    </td>
                                )}
                            </tr>
                        )
                    })}
                </tbody>
            </table>
        </>
    )
}