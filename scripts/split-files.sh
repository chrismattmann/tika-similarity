#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# originally taken from:
# https://stackoverflow.com/questions/29116212/split-a-folder-into-multiple-subfolders-in-terminal-bash-script

i=0;

mydir=$1
size=$2

for f in ${mydir}/*; do
    d=dir_$(printf %03d $((i/${size}+1)));
    mkdir -p $d;
    mv "$f" $d;
    let i++;
done
