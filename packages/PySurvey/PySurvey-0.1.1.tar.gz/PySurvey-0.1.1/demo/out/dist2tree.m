function tree = dist2tree(Dfile)
% Build a phylogenetic tree object from distance matrix.

%% parse the input file
input = importdata(Dfile, '\t');
D = input.data; % distance matrix 
names = input.textdata(2:end,1); % leaf names

%% make the tree
method = 'average'; % linkage method for cluster. 
tree = seqlinkage(D, method, names);