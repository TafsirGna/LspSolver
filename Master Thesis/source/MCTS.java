package main;

import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedList;
import java.util.Map;
import java.util.Random;

public class MCTS {

    private Node rootNode;
    private double explorationConstant = Math.sqrt(2.0);

    public MCTS() {
    }
    public Move runMCTS(Board startingBoard, int runs, boolean bounds, boolean ucbStandard) {
    }
    private Map.Entry<Board, Node> treePolicy(Board b, Node node) {
    }
    private double[] playout(Node state, Board board, boolean ucbStandard) {
    }
    private Move finalMoveSelection(Board b, Node n) {
    }

}
