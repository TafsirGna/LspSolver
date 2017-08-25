package main;

import java.util.ArrayList;
import java.util.Set;

public class Node {

    public double[] score;
    public double games;
    public Move move;
    public ArrayList<Node> unvisitedChildren;
    public ArrayList<Node> children;
    public Node parent;
    public int player;
    public double[][] infoTab;
    public int number;
    public char[][] pieces;
    
    public Node(Board b) {
    }
    public void printinfo() {
    }
    public Node(Board b, Move m, Node prnt) {
    }
    public double upperConfidenceBound(double c) {
    }
    public double stateEvaluation() {
    }
    public void backPropagateScore(double[] scr) {
    }
    public void expandNode(Board currentBoard) {
    }
    public void compute() {
    }
}
