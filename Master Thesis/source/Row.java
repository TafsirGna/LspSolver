private void checkRows(int row, char[][] t) {
    for (int i = 0; i < t.length; i++) {
      if (t[row][i] == ' ' || t[row][i] == ((player == 1) ? 'O' : 'X')) {
	continue;
      }
      if (i - 1 >= 0 && ((t[row][i - 1] == ((player == 1) ? 'X' : 'O')))) {
	continue;
      }

      int nbre = 1, v1, v2;
      int saut = 0;
      for (v1 = i, v2 = i + 1; v2 < t.length;) {
	if ((t[row][v1] == t[row][v2])) {
	  nbre++;
	  if (v2 + 1 < t.length && ((t[row][v2] == t[row][v2 + 1]) || (t[row][v2 + 1] == ' '))) {
	    v1 = v2;
	    v2++;
	  } else {
	    break;
	  }
	} else if (t[row][v2] == ' ') {
	  saut++;
	  if (saut < 2) {
	    if (v2 + 1 < t.length) {
	      if (t[row][v1] == t[row][v2 + 1]) {
		v2++;
	      } else {
		v2--;
		break;
	      }
	    } else {
	      v2--;
	      break;
	    }
	  } else {
	    v2--;
	    break;
	  }
	} else {
	  v2--;
	  break;
	}
      }
      int init = i;
      int fin = v2;
    }
}
