set -ex
export  R05CCOMP="clang -o main"
cd build && refal05c ../src/* ../lib/* Library LibraryEx refal05rts
