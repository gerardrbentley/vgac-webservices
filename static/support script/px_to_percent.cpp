#include<iostream>
#include<string>
#include <bits/stdc++.h>
using namespace std;
void line_changer(string s)
{
    size_t px = s.find("px");
    size_t top = s.find("top:");
    size_t left = s.find("left:");
    size_t height = s.find("height:");
    size_t width = s.find("width:");
    string tmp = "";
    int temp = 0;
    double num = 0.0;
    if (top != std::string::npos)
    {
        tmp = s.substr(top+4, px - top - 4); //px number
        temp = stoi(tmp);
        num = temp;
        num = round(num/768 * 1000.0)/1000;
        tmp = to_string(num*100);
        tmp += "%;";
        s.replace(top + 4, 100, tmp); 
        cout << s << "\n";
        return;
    }
    if (left != std::string::npos)
    {
        tmp = s.substr(left+5, px - left - 5); //px number
        temp = stoi(tmp);
        num = temp;
        num = round(num/1440 * 1000.0)/1000;
        tmp = to_string(num*100);
        tmp += "%;";
        s.replace(left + 5, 100, tmp); 
        cout << s << "\n";
        return;
    }
    if (height != std::string::npos)
    {
        tmp = s.substr(height+7, px - height - 7); //px number
        temp = stoi(tmp);
        num = temp;
        num = round(num/768 * 1000.0)/1000;
        tmp = to_string(num*100);
        tmp += "%;";
        s.replace(height + 7, 100, tmp); 
        cout << s << "\n";
        return;
    }
    if (width != std::string::npos)
    {
        tmp = s.substr(width+6, px - width - 6); //px number
        temp = stoi(tmp);
        num = temp;
        num = round(num/1440 * 1000.0)/1000;
        tmp = to_string(num*100);
        tmp += "%;";
        s.replace(width + 6, 100, tmp); 
        cout << s << "\n";
        return;
    }
    tmp = "";
    temp = 0;
    num = 0.0;
    cout << s << "\n";
    
}
 
int main(){
  int lines;
  cin >> lines;
  string tmp;
  for (int i = 0; i < lines; i++)
  {
    cin >> tmp;
    line_changer(tmp);
  }
  return 0;
}