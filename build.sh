set -ex
shopt -s globstar

export R05CCOMP="clang -lpq -o main"
cd build && refal05c ../src/**/*.ref ../lib/**/*.ref ../lib/**/*.c Library LibraryEx refal05rts
