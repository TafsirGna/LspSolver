package main;

import java.awt.Point;
import java.util.ArrayList;

public abstract class Board {

    protected int currentPlayer;
    protected int winner;
    protected boolean draw;
    protected boolean gameWon;
    protected int freeslots;
    protected ArrayList<Piece> playerOnePieces;
    protected ArrayList<Piece> playerTwoPieces;
    protected int xlength;
    protected int ylength;
    protected int number;
    
    public abstract Board duplicate();
    public char[][] makeTab() {
    }
    public ArrayList<Move> getMoves() {
    }
    public void makeMove(Move move) {
    }
    public boolean isGameOver() {
    }
    public boolean isSolved() {
    }
    public int getCurrentPlayer() {
    }
    public double[] getScore() {
    }
    public void bPrint() {
    }
}