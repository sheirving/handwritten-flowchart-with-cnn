from graph import Graph
from node import Node
import os
class CodeGenerator(object):
    def __init__(self,image_path = None,result_path = None):
        self.result_path = result_path
        t1 = Node(coordinate = [384,600,123,189],text = "inicio")
        t2 = Node(coordinate = [375,597,378,438],text = "x=6")
        t3 = Node(coordinate = [429,570,678,750],text = "x>5")
        t4 = Node(coordinate = [402,579,960,1008],text = '"falso"')
        t5 = Node(coordinate = [783,930,948,1008],text = '"verdad"')
        t6 = Node(coordinate = [426,546,1341,1410],text = "fin")
        t7 = Node(coordinate = [705,825,606,666],text = "si")
        t8 = Node(coordinate = [363,423,858,906],text = "no")

        s1 = Node(coordinate = [318,675,81,231],class_shape = "start_end")
        s2 = Node(coordinate = [456,513,237,354],class_shape = "arrow_line_down")
        s3 = Node(coordinate = [306,684,354,489],class_shape = "process")
        s4 = Node(coordinate = [462,522,483,594],class_shape = "arrow_line_down")
        s5 = Node(coordinate = [345,615,588,858],class_shape = "decision")
        s6 = Node(coordinate = [612,921,702,939],class_shape = "arrow_rectangle_down",image_path="graph_images/rect_down.png")
        s7 = Node(coordinate = [438,504,849,954],class_shape = "arrow_line_down")
        s8 = Node(coordinate = [372,645,948,1125],class_shape = "print")
        s9 = Node(coordinate = [741,1059,936,1095],class_shape = "print")
        s10 = Node(coordinate = [420,471,1119,1320],class_shape = "arrow_line_down")
        s11 = Node(coordinate = [669,849,1092,1410],class_shape = "arrow_rectangle_right",image_path="graph_images/rect_right.png")
        s12 = Node(coordinate = [339,669,1317,1455],class_shape = "start_end")


        self.graph = Graph([t1,t2,t3,t4,t5,t6,t7,t8],[s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12])

        self.adj_list = self.graph.generate_graph()
        print("adjacency_list = ",self.adj_list)
        self.nodes = self.graph.get_nodes()
        self.pos_x = 0
        #ponter list to know how tabs need to white
        self.pointer_x_list = [0]*5
        self.lines_to_write = []
        self.variables = []
        self.type_map = {"int":"%d","double":"%f","char":"%c"}
    def is_any_arrow(self,node):
        return node.get_class().split('_')[0] == "arrow"
    def generate_tabs(self,pos_x):
        return "    "*pos_x

    def get_type(self,sentence):
        tam_data = {"char":1,"int":2,"double":8}
        separated = []
        pos = 0
        i = 0
        while(i < len(sentence)):
            x = sentence[i]
            print("i",sentence[i])
            if(x == '+' or x == '-' or x == '/' or x == '*' or x == '%' or x == '<' or x == '>' or x == '^' or x == '='):
                separated.append(str(sentence[pos:i]))
                pos = i + 1
            i += 1
        separated.append(sentence[pos:len(sentence) + 1])
        for i in range(len(separated)):
            if("(" in separated[i]):
                separated[i] = separated[i].replace('(', '')
            if(")" in separated[i]):
                separated[i] = separated[i].replace(')', '')
        maxi = float('-inf')
        max_data = None
        for i in range(len(separated)):
            if(separated[i][0] == '"' and separated[i][-1] == '"'):
                return '"%s"'
            x = list(filter(lambda x: (x[0] == separated[i]), self.variables))
            print("Erooor x",x)
            if(len(x) > 0):
                if(tam_data[x[0][1]] > maxi):
                    maxi = tam_data[x[0][1]]
                    max_data = x[0][1]
            else:
                if(len(separated[i]) == 1 and separated[i].isalpha()):
                    maxi = tam_data["char"]
                    max_data = "char"
                try:
                    int(separated[i])
                    maxi = tam_data["int"]
                    max_data = "int"
                except ValueError:
                    try:
                        float(separated[i])
                        maxi = tam_data["double"]
                        max_data = "double"
                    except ValueError:
                        return ""

            return '"'+self.type_map[max_data]+'"'
    def predict_type(self,sentence):
        def type_variable(s):
            if(len(sentence) == 1 and sentence.isalpha()):
                return "char"
            try:
                int(s)
                return "int"
            except ValueError:
                try:
                    float(s)
                    return "double"
                except ValueError:
                    return ""
        if("=" in sentence):
            var = [s.split('=')[0] for s in sentence.split(',')]
            value = [s.split('=')[1] for s in sentence.split(',')]
            pos = 0

            flag = True
            for i in range(len(var)):
                if(len(list(filter(lambda x: (x[0] == var[i]), self.variables))) == 0):
                    self.variables.append([var[i],type_variable(value[i])])
                else:
                    flag = False
                    #aux = type_variable(value[i])
                    #sentence = sentence[0:pos] + aux + sentence[pos:len(sentence)]
                    #pos += len(aux)+len(var[i]) + len(value[i]) + 2
            if(flag):
                return type_variable(value[0]) +" "+ sentence
            return sentence
        else:
            return sentence
    #Generate the code of the graph
    def generate(self,index,end_x):
        if(end_x != index):
            #The node 0 is the start end
            if(index == 0):
                #Is is diferent to Not valid
                if(self.adj_list == "Not valid"):
                    return False
                #Start to write the code
                self.lines_to_write.append("#include<stdio.h>\n")
                self.lines_to_write.append("int main(){\n")
                self.pos_x += 1
                #Call the function with the next node
                self.generate(self.adj_list[index][0],end_x)
            #Is is a arrow
            elif(self.is_any_arrow(self.nodes[index])):
                #Call the function with the next node
                self.generate(self.adj_list[index][0],end_x)
            #If is a process node
            elif(self.nodes[index].get_class() == "process"):
                self.lines_to_write.append(self.generate_tabs(self.pos_x)+self.predict_type(self.nodes[index].get_text())+";\n")
                #Call the function with the next node
                self.generate(self.adj_list[index][0],end_x)
            elif(self.nodes[index].get_class() == "scan"):
                self.lines_to_write.append(self.generate_tabs(self.pos_x)+'scanf("'+self.type_map[list(filter(lambda x: (x[0] == self.nodes[index].get_text()), self.variables))[0][1]]+'",&'+self.nodes[index].get_text()+');\n')
                self.generate(self.adj_list[index][0],end_x)
            elif(self.nodes[index].get_class() == "print"):
                #change the form to get tthe type
                self.lines_to_write.append(self.generate_tabs(self.pos_x)+'printf('+self.get_type(self.nodes[index].get_text())+','+self.nodes[index].get_text()+');\n')
                self.generate(self.adj_list[index][0],end_x)
            elif(self.nodes[index].get_class() == "start_end" and self.nodes[index].get_text()):
                self.lines_to_write.append(self.generate_tabs(self.pos_x)+"return 0;\n");
                self.lines_to_write.append("}\n");
                f = open(self.result_path, "a")
                f.writelines(self.lines_to_write)
                f.close()
            elif(self.nodes[index].get_class() == "decision"):
                #find a path tyo the same node
                visited_list = [0]*len(self.nodes)
                def dfs(v,c):
                    if(v == index):
                        c += 1
                    if(c > 1):
                        return True,v
                    else:
                        visited_list[v] += 1
                        for i in self.adj_list[v]:
                            if(visited_list[i] <= 1):
                                return dfs(i,c)
                ans = dfs(index,0)
                if(ans == None):
                    #it is a if
                    self.lines_to_write.append(self.generate_tabs(self.pos_x)+"if("+self.nodes[index].get_text()+"){\n")
                    self.pos_x += 1
                    def dfs2(v,visited):
                        visited[v] = 1
                        for i in self.adj_list[v]:
                            if(visited[i] == 0):
                                dfs2(i,visited)
                        return visited
                    yes_path = -1
                    no_path = -1
                    for i in self.adj_list[index]:
                        if(self.nodes[i].get_text() == "si"):
                            yes_path = self.adj_list[index].index(i)
                    for i in self.adj_list[index]:
                        if(self.nodes[i].get_text() == "no"):
                            no_path = self.adj_list[index].index(i)
                    yes_visited = dfs2(self.adj_list[index][yes_path],[0]*len(self.nodes))
                    no_visited = dfs2(self.adj_list[index][no_path],[0]*len(self.nodes))
                    stop = -1
                    for i in range(len(yes_visited)):
                        if(yes_visited[i] == 1 and no_visited[i] == 1):
                            stop = i
                            break
                    yes_stop = -1
                    print("stop",stop,yes_visited,no_visited)
                    for i in reversed(range(stop)):
                        if(yes_visited[i] == 1):
                            yes_stop = i
                            break
                    no_stop = -1
                    for i in reversed(range(stop)):
                        if(no_visited[i] == 1):
                            no_stop = i
                            break
                    print("YESSS NOOO",yes_stop,no_stop)
                    self.generate(self.adj_list[index][yes_path],yes_stop)
                    self.pos_x -= 1
                    self.lines_to_write.append(self.generate_tabs(self.pos_x)+"}\n")
                    self.lines_to_write.append(self.generate_tabs(self.pos_x)+"else{\n")
                    self.pos_x += 1
                    self.generate(self.adj_list[index][no_path],no_stop)
                    self.pos_x -= 1
                    self.lines_to_write.append(self.generate_tabs(self.pos_x)+"}\n")
                    self.generate(stop,-1)
                elif(ans[0] == True):
                    self.lines_to_write.append(self.generate_tabs(self.pos_x)+"while("+self.nodes[index].get_text()+"){\n")
                    self.pos_x += 1
                    end = ans[1]
                    start = -1
                    for i in self.adj_list[index]:
                        if(self.nodes[i].get_text() == "si"):
                            start = self.adj_list[index].index(i)
                    self.generate(self.adj_list[index][start],end)
                    self.pos_x -= 1
                    self.lines_to_write.append(self.generate_tabs(self.pos_x)+"}\n")
                    for i in self.adj_list[index]:
                        if(self.nodes[i].get_text() == "no"):
                            start = self.adj_list[index].index(i)
                    self.generate(self.adj_list[index][start],-1)
cg = CodeGenerator(result_path = "result1.c")
cg.generate(0,-1)
