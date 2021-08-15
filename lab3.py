import sys
import csv
import collections
import math
from statistics import mode

class Node:
    def __init__(self, feature, subtree):
        self.feature = feature
        self.subtree = subtree

class Leaf:
    def __init__(self, value):
        self.value = value
    

class ID3:
    def __init__(self, *depth):
        self.depth = float("inf")
        if depth:
            self.depth = int(depth[0])
        self.data = []
    
    
    def fit(self, train_set):
        features = {}
        labels = [x[-1] for x in train_set]

        for i,f in enumerate(train_set.pop(0)):
            features[(f,i)] = set()
            for v in train_set:
                features[(f,i)].add(v[i])
            features[(f,i)] = sorted(list(features[(f,i)]))

        features.popitem()
        labels = labels[1:]
        self.tree = self.id3_alg(train_set, train_set, features, labels, 0, self.depth)


    def predict(self, test_set):
        predictions = []
        features = test_set.pop(0)
        features = features[:-1]
        original = []

        for row in test_set:
            sample = {}
            original.append(row[-1])
            for f,r in zip(features,row[:-1]):
                sample[f]=r
            predictions.append(self.predict_alg(sample,self.tree))

        out = '[PREDICTIONS]:'
        for p in predictions:
            out+= ' ' + p
        print(out)

        acc=0
        for i,j in zip(original, predictions):
            if i==j:
                acc+=1
        acc = acc/len(original)
        print(f'[ACCURACY]: {acc:.5f}')

        print('[CONFUSION_MATRIX]:')
        labels = sorted(list(set(original)))
        matrix = {}

        for l1 in labels:
            tmp = []
            for l2 in labels:
                tmp.append(0)
                matrix[(l1,l2)]=0

        for i,j in zip(original, predictions):
            matrix[(i,j)]+=1
        
        out = ''
        c=0
        for v in matrix.values():
           out+= str(v) + ' '
           c+=1
           if c%len(labels)==0:
               print(out[:-1])
               out = '' 
        return predictions

    
    def predict_alg(self, sample, tree):
        if isinstance(tree,Leaf):
            return tree.value
        c=0
        for t in tree.subtree:
            c+=1
            if t[0] == sample[tree.feature[0]]:
                return self.predict_alg(sample, t[1])
        
        if c == len(tree.subtree):
            labels = []
            for i,t in enumerate(tree.subtree):
                labels.append(self.predict_alg(sample,t[1]))
            return(mode(sorted(labels)))

    def id3_alg(self, D, D_parent, features, labels, depth, max_depth):
        if len(set(labels)) == 1:
            return labels[0]

        if not D or max_depth == 0:
            count_dict = {}
            for y in D_parent:
                if y[-1] not in count_dict.keys():
                    count_dict[y[-1]]=1
                else:
                    count_dict[y[-1]]+=1
            count_dict = collections.OrderedDict(sorted(count_dict.items()))
            v = max(count_dict, key=count_dict.get)
            return Leaf(v)
        
        count_dict = {}
        for y in D:
            if y[-1] not in count_dict.keys():
                count_dict[y[-1]]=1
            else:
                count_dict[y[-1]]+=1
        count_dict = collections.OrderedDict(sorted(count_dict.items()))
        v = max(count_dict, key=count_dict.get)
        
        D_y = [x for x in D if x[-1] == v]

        if not features.keys() or D == D_y or depth==max_depth:
            return Leaf(v)
        
        ig_dict = self.IG(D,features)
        x = max(ig_dict, key=ig_dict.get)
        subtrees = []
        features_new = features.copy()
        del features_new[x]

        for value in features[x]:
            D_x = [i for i in D if i[x[1]] == value]
            if depth+1<=max_depth:
                t = self.id3_alg(D_x ,D,features_new,labels,depth+1, max_depth)
                subtrees.append((value, t))
            else:
                t = self.id3_alg(None ,D,features_new,labels,depth+1, max_depth)
        
        return Node(x, subtrees)

    def entropy(self, D):
        labels_all = []
        for l in D:
            labels_all.append(l[-1])
        labels = set(labels_all)
        e=0
        for l1 in labels:
            c = 0
            for l2 in labels_all:
                if l1 == l2:
                    c+=1
            e+=(c/len(labels_all))*math.log2(c/len(labels_all))
        return -1*e

    def IG(self, D, X):
        ig_dict = {}
        self.entropy(D)
        for idx,i in enumerate(X):
            ig_dict[i] = self.entropy(D) 
            v = X[i]
            for v_i in v:
                d_i = []
                for d in D:
                    if d[i[1]]==v_i:
                        d_i.append(d)
                ig_dict[i] -= len(d_i)/len(D)*self.entropy(d_i) 
            
        ig_dict = collections.OrderedDict(sorted(ig_dict.items()))
        return(ig_dict)

    def print_tree(self, tree, out, level):
        if not isinstance(tree,Leaf):
            for i,t in enumerate(tree.subtree):
                send = out + f'{level}:{tree.feature[0]}={t[0]} '
                self.print_tree(t[1], send, level+1)
        else:
            out+= tree.value
            print(out)


if __name__ == "__main__":
    arguments = len(sys.argv) - 1
    train_path = sys.argv[1]
    test_path = sys.argv[2]
    if arguments == 3:
        depth = sys.argv[3]
        model = ID3(depth)
    else:
        model = ID3()

    train_set = []
    test_set = []

    with open(train_path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            train_set.append(row)

    with open(test_path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            test_set.append(row)
    
    model.fit(train_set)
    tree = model.tree
    print('[BRANCHES]:')
    model.print_tree(model.tree, '', 1)
    model.predict(test_set)

    