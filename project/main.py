
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import sys
import platform
from datetime import datetime

import mysql.connector
from mysql.connector import Error

from backend.user_manager import (
    register_user, login_user, get_user_profile, update_user_profile,
    search_users, add_friend, remove_friend, get_friends_list, update_friend_group,
    get_minimal_user_directory
)
from backend.moment_manager import (
    post_moment, update_moment, delete_moment,
    get_my_moments, get_friends_moments, add_comment, delete_comment
)
from backend.admin_manager import (
    login_admin, get_admin_profile, update_admin_profile,
    get_all_users, delete_user_by_admin, get_all_moments_for_review, delete_moment_by_admin
)


class mySocialNetwork:
    """main class"""
    
    def __init__(self):
        self.current_user = None  # {'user_id': int, 'username': str, 'role': 'user'|'admin'}
        self.running = True
    
    def clear_screen(self):
        print("\n" * 50)
    
    def print_header(self):
        """header"""
        print("*" * 80)
        print(" " * 10 + "Simple Social Network Platform - By Hou Fanbo & Gong Xi")
        print("*" * 80)
        if self.current_user:
            role_str = "[ADMIN]" if self.current_user['role'] == 'admin' else "[USER]"
            print(f"You are {role_str}{self.current_user['username']} (ID: {self.current_user['id']})")
        else:
            print("You haven't logged in yet.")
        print("-" * 60)
    
    def get_input(self, prompt: str, required: bool = True) -> str:
        """get user input"""
        while True:
            value = input(f"> {prompt}: ").strip()
            if value.lower() == 'q':
                return None
            if not required or value:
                return value
            print("> No input was detected. Please re-enter.")
    
    def get_int_input(self, prompt: str, required: bool = True) -> int:
        """get an integer"""
        while True:
            value = self.get_input(prompt, required)
            if value is None:
                return None
            try:
                return int(value)
            except ValueError:
                print("> Invaild interger!")
    
    def confirm_action(self, message: str) -> bool:
        """confirm"""
        choice = input(f"> {message} (y/n): ").strip().lower()
        return choice == 'y'
    
    # ==================== main cycle ====================
    
    def run(self):
        """runner"""
        while self.running:
            self.clear_screen()
            self.print_header()
            
            if not self.current_user:                   # logout state
                self.show_login_menu()
            elif self.current_user['role'] == 'user':   # user
                self.show_user_menu()
            else:                                       # admin
                self.show_admin_menu()
    
    # ==================== logout menu ====================
    
    def show_login_menu(self):
        """show login/register menu"""
        print("\n Welcome, please enter an integer to select an operation. ")
        print("  1. user register")
        print("  2. user login")
        print("  3. admin login")
        print("  0. exit")
        
        choice = self.get_input("\n> enter an integer(0-3): ")
        
        if choice == '1':
            self.handle_register()
        elif choice == '2':
            self.handle_user_login()
        elif choice == '3':
            self.handle_admin_login()
        elif choice == '0':
            self.running = False
            print("\n> EXIT")
        else:
            print("> Invaild input!")
            input("> press enter to continue...")
    
    def handle_register(self):
        """user register"""
        print("\n user registering...")
        username = self.get_input("> Please enter your username: ")
        if not username:
            return
        
        password = self.get_input("> Please enter your password: ")
        if not password:
            return
        
        result = register_user(username, password)
        
        if result['success']:
            print(f">> {result['message']}")
            print(f" Your ID: {result['user_id']}")
            input("  Press enter to return...")
        else:
            print(f"> {result['message']}")
            input("  Press enter to return...")
    
    def handle_user_login(self):
        """user login"""
        print("\n user logging in...")
        username = self.get_input("> Please enter your username: ")
        if not username:
            return
        
        password = self.get_input("> Please enter your password: ")
        if not password:
            return
        
        result = login_user(username, password)
        
        if result['success']:
            self.current_user = {
                'id': result['user_id'],
                'username': username,
                'role': 'user'
            }
            print(f">> {result['message']}. {result['name']}, welcome back.")
            input("  Press enter to return...")
        else:
            print(f"> {result['message']}")
            input("  Press enter to return...")
    
    def handle_admin_login(self):
        """admin login"""
        print("\n admin logging in...")
        admin_username = self.get_input("> Please enter your username:")
        if not admin_username:
            return
        
        password = self.get_input("> Please enter your password:")
        if not password:
            return
        
        result = login_admin(admin_username, password)
        
        if result['success']:
            self.current_user = {
                'id': result['admin_id'],
                'username': admin_username,
                'role': 'admin'
            }
            print(f">> {result['message']}. {result['name']} administrator successfully logged in.")
            input("  Press enter to enter admin menu.")
        else:
            print(f"> {result['message']}")
            input("  Press enter to return...")
    
    # ==================== user menu ====================
    
    def show_user_menu(self):
        """show user menu"""
        print("\n USER MENU")
        print("1. Personal information")
        print("2. Friends")
        print("3. Moments")
        print("4. Logout")
        print("0. Exit")
        
        choice = self.get_input("\n > enter an integer(0-4): ")
        
        if choice == '1':
            self.show_user_profile_menu()
        elif choice == '2':
            self.show_friend_menu()
        elif choice == '3':
            self.show_moment_menu()
        elif choice == '4':
            self.current_user = None
            print("> Logout")
            input("  Press enter to return...")
        elif choice == '0':
            self.running = False
            print("\n> EXIT")
        else:
            print("> Invaild input!")
            input("> press enter to continue...")
    
    def show_user_profile_menu(self):
        """personal info"""
        while True:
            self.clear_screen()
            self.print_header()
            print("\n> Personal Info")
            
            profile = get_user_profile(self.current_user['id'])
            if profile:
                print(f"  name: {profile.get('name', '?')}")
                print(f"  gender: {profile.get('gender', '?')}")
                print(f"  birth: {profile.get('birth_date', '?')}")
                print(f"  age: {profile.get('age', '?')}")
            else:
                print("> No data..?")
            
            print("\n Operation: ")
            print("1. modify your personal infomation")
            print("0. return")
            
            choice = self.get_input("\n> enter an integer(0-1): ")
            
            if choice == '1':
                self.handle_update_profile()
            elif choice == '0':
                break
            else:
                print("> Invaild input!")
                input("> press enter to continue...")
    
    def handle_update_profile(self):
        """upd personal info"""
        print("\n> Modify your personal infomation")
        
        name = self.get_input("name", required=False)
        gender = self.get_input("gender", required=False)
        birth_date = self.get_input("birth", required=False)
        
        if not any([name, gender, birth_date]):
            print("> Invaild input!")
            input("> press enter to continue...")
            return
        
        result = update_user_profile(
            self.current_user['id'],
            name=name if name else None,
            gender=gender if gender else None,
            birth_date=birth_date if birth_date else None
        )
        
        if result['success']:
            print(f">> {result['message']}")
        else:
            print(f"> {result['message']}")
        input("> press enter to continue...")
    
    def show_friend_menu(self):
        """friends"""
        while True:
            self.clear_screen()
            self.print_header()
            print("\n  FRIENDS")
            print("1. View user directory") 
            print("2. Search users")                  
            print("3. Add friends")                   
            print("4. View my friends")               
            print("5. Delete friends")                
            print("6. Modify friend groups")       
            print("0. Return")

            choice = self.get_input("\n> enter an integer(0-6): ") 

            if choice == '1':
                self.handle_view_user_directory()    
            elif choice == '2':
                self.handle_search_users()
            elif choice == '3':
                self.handle_add_friend()
            elif choice == '4':
                self.handle_view_friends()
            elif choice == '5':
                self.handle_remove_friend()
            elif choice == '6':
                self.handle_update_friend_group()
            elif choice == '0':
                break
            else:
                print("> Invaild input!")
                input("> press enter to continue...")
    
    def handle_view_user_directory(self):
        """users"""
        self.clear_screen()
        print("\n" + "="*15 + " User Directory " + "="*15)

        users = get_minimal_user_directory()
        
        if users:
            print(f"{'ID':<10}{'Username':<20}")
            print("-" * 35)
            for u in users:
                if u['user_id'] == self.current_user['id']:
                    continue
                print(f"{u['user_id']:<10}{u['username']:<20}")
            print("-" * 35)
        else:
            print("  ~> No other users.")
            
        print("\n1. Enter ID to add friend")
        print("2. Return")
        choice = input("> Select operation (1-2): ").strip()
        
        if choice == '1':
            friend_id = self.get_int_input("Please enter the user ID you want to add: ")
            if friend_id:
                if friend_id == self.current_user['id']:
                    print("  > You cannot add yourself as a friend.")
                else:
                    group_name = self.get_input("> Please enter the name of the friend group: ", required=False)

                    result = add_friend(
                        self.current_user['id'], 
                        friend_id,
                        group_name if group_name else "默认分组" 
                    )      
                    if isinstance(result, dict) and 'message' in result:
                        print(f"  >> {result['message']}")
                    else:
                        print("  >> Success.")
            input("\n> press enter to continue...")
        else:
            return
        
    def handle_search_users(self):
        """search users"""
        print("\n> Search users")
        keyword = self.get_input(" Please enter the search keyword (username):")
        if not keyword:
            return
        
        results = search_users(keyword)
        
        if results:
            print(f"\n>> Finds {len(results)} users: ")
            print("-" * 50)
            for user in results:
                print(f"  ID: {user['user_id']:4d} | username: {user['username']:15s}")
            print("-" * 50)
        else:
            print("> No matching user found.")
        
        input("  > press enter to return...")
    
    def handle_add_friend(self):
        """add a friend"""
        print("\n> Add a friend")
        friend_id = self.get_int_input(" Please enter the user ID: ")
        if friend_id is None:
            return
        
        group_name = self.get_input("> Please enter the name of the friend group: ", required=False)
        
        result = add_friend(
            self.current_user['id'],
            friend_id,
            group_name if group_name else "default group"
        )
        
        if result['success']:
            print(f">> {result['message']}")
        else:
            print(f"> {result['message']}")
        input("  > press enter to return...")
    
    def handle_view_friends(self):
        """my friends list"""
        print("\n> Friends list")
        group_filter = self.get_input("> Please enter the name of the group you want to view: ", required=False)
        
        friends = get_friends_list(self.current_user['id'], group_filter if group_filter else None)
        
        if friends:
            print(f"\n>> get {len(friends)} friends: ")
            print("-" * 60)
            print(f"{'ID':<6} {'username':<15} {'name':<10} {'group':<15}")
            print("-" * 60)
            for friend in friends:
                print(f"{friend['friend_id']:<6} {friend['username']:<15} {friend['name']:<10} {friend['group_name']:<15}")
            print("-" * 60)
        else:
            print(">  No friends" if not group_filter else f"  > There's no friend in group '{group_filter}'.")
        
        input("  > press enter to return...")
    
    def handle_remove_friend(self):
        """delete a friend"""
        print("\n> Delete a friend")
        friend_id = self.get_int_input("> Please enter the ID of the friend you want to delete: ")
        if friend_id is None:
            return
        
        if not self.confirm_action("  Delete the friend?"):
            print("  > Canceled.")
            input("  > press enter to return...")
            return
        
        result = remove_friend(self.current_user['id'], friend_id)
        
        if result['success']:
            print(f">> {result['message']}")
        else:
            print(f"> {result['message']}")
        input("  > press enter to return...")
    
    def handle_update_friend_group(self):
        """modify friend groups"""
        print("\n> Modify friend groups")
        friend_id = self.get_int_input(">  Please enter the ID of the friend: ")
        if friend_id is None:
            return
        
        new_group = self.get_input("> Please enter the new group name: ")
        if not new_group:
            return
        
        result = update_friend_group(self.current_user['id'], friend_id, new_group)
        
        if result['success']:
            print(f">> {result['message']}")
        else:
            print(f"> {result['message']}")
        input("  > press enter to return...")
    
    def show_moment_menu(self):
        """moments menu"""
        while True:
            self.clear_screen()
            self.print_header()
            print("\n MOMENTS MENU")
            print("1. Post on the moments")
            print("2. View my moments")
            print("3. View my friends' moments")
            print("4. Modify my moments")
            print("5. Delete my moments")
            print("6. Comment on the moments")
            print("7. Delete my comments")
            print("0. Return")
            
            choice = self.get_input("\n> enter an integer(0-7): ")
            
            if choice == '1':
                self.handle_post_moment()
            elif choice == '2':
                self.handle_view_my_moments()
            elif choice == '3':
                self.handle_view_friends_moments()
            elif choice == '4':
                self.handle_update_moment()
            elif choice == '5':
                self.handle_delete_moment()
            elif choice == '6':
                self.handle_add_comment()
            elif choice == '7':
                self.handle_delete_comment()
            elif choice == '0':
                break
            else:
                print("> Invaild input!")
                input("> press enter to continue...")
    
    def handle_post_moment(self):
        """post on moments"""
        print("\n> Post on moments")
        content = self.get_input("> Please enter the content (maximum 500 words): ")
        if not content:
            return
        
        if len(content) > 500:
            print("  > Word limit exceed.")
            input("  > press enter to return...")
            return
        
        result = post_moment(self.current_user['id'], content)
        
        if result['success']:
            print(f">> {result['message']}")
            print(f"   Moment ID: {result['moment_id']}")
        else:
            print(f"> {result['message']}")
        input("  > press enter to return...")
    
    def handle_view_my_moments(self):
        """view my moments"""
        print("\n> View my moments")
        
        moments = get_my_moments(self.current_user['id'])
        
        if moments:
            print(f"\n>> Get {len(moments)} moments: ")
            print("-" * 70)
            for moment in moments:
                print(f"ID: {moment['moment_id']} | {moment['last_update_time']}")
                print(f"   {moment['content']}")
                print(f"   comments: {moment['comment_count']}")
                print("-" * 70)
        else:
            print("> No moments.")
        
        input("  > press enter to return...")
    
    def handle_view_friends_moments(self):
        """view my friend moments"""
        print("\n> View my friend moments")
        
        moments = get_friends_moments(self.current_user['id'])
        
        if moments:
            print(f"\n>> Get {len(moments)} friend moments: ")
            print("=" * 70)
            for moment in moments:
                print(f"\n {moment['username']}: ")
                print(f" Moment ID: {moment['moment_id']} | {moment['last_update_time']}")
                print(f"   {moment['content']}")
                
                if moment['comments']:
                    print(f"\n  .>>  Get ({len(moment['comments'])} comments):")
                    for comment in moment['comments']:
                        print(f"   - {comment['commenter_name']}: {comment['content']} ({comment['comment_time']})")
                else:
                    print("   .>  No comments.")
                
                print("=" * 70)
        else:
            print("  >No friend moments.")
        
        input("  > press enter to return...")
    
    def handle_update_moment(self):
        """modify moments"""
        print("\n> Modify my moments")
        moment_id = self.get_int_input("> Please enter the ID of the moment you want to modify: ")
        if moment_id is None:
            return
        
        new_content = self.get_input("> Please enter the new content (maximum 500 words): ")
        if not new_content:
            return
        
        if len(new_content) > 500:
            print("  > Word limit exceed.")
            input("  > press enter to return...")
            return
        
        result = update_moment(moment_id, self.current_user['id'], new_content)
        
        if result['success']:
            print(f">> {result['message']}")
        else:
            print(f"> {result['message']}")
        input("  > press enter to return...")
    
    def handle_delete_moment(self):
        """delete moments"""
        print("\n> Delete my moments")
        moment_id = self.get_int_input("> Please enter the ID of the moment you want to delete: ")
        if moment_id is None:
            return
        
        if not self.confirm_action("  Confirm? Once deleted, the related comments will also be removed."):
            print("  > Canceled.")
            input("  > press enter to return...")
            return
        
        result = delete_moment(moment_id, self.current_user['id'])
        
        if result['success']:
            print(f">> {result['message']}")
        else:
            print(f"> {result['message']}")
        input("  > press enter to return...")
    
    def handle_add_comment(self):
        """comment on mements"""
        print("\n> Comment on mements")
        moment_id = self.get_int_input("> Please enter the ID of the moment you want to comment: ")
        if moment_id is None:
            return
        
        content = self.get_input("> Please enter the comment (maximum 255 words): ")
        if not content:
            return
        
        if len(content) > 255:
            print("  > Word limit exceed.")
            input("  > press enter to return...")
            return
        
        result = add_comment(moment_id, self.current_user['id'], content)
        
        if result['success']:
            print(f">> {result['message']}")
            print(f"   comment ID: {result['comment_id']}")
        else:
            print(f"> {result['message']}")
        input("  > press enter to return...")
    
    def handle_delete_comment(self):
        """delete my comment"""
        print("\n> Delete my comment")
        comment_id = self.get_int_input("> Please enter the ID of the comment you want to delete: ")
        if comment_id is None:
            return
        
        if not self.confirm_action("  Confirm? "):
            print("  > Canceled.")
            input("  > press enter to return...")
            return
        
        result = delete_comment(comment_id, self.current_user['id'])
        
        if result['success']:
            print(f">> {result['message']}")
        else:
            print(f"> {result['message']}")
        input("  > press enter to return...")
    
    # ==================== Admin menu ====================
    
    def show_admin_menu(self):
        """admin menu"""
        print("\n~~ ADMIN MENU ~~")
        print("1. Personal Infomation")
        print("2. User Managements")
        print("3. Moment Review")
        print("4. Log out")
        print("0. Exit")
        
        choice = self.get_input("\n~> enter an integer(0-4):  ")
        
        if choice == '1':
            self.show_admin_profile_menu()
        elif choice == '2':
            self.show_admin_user_management()
        elif choice == '3':
            self.show_admin_moment_review()
        elif choice == '4':
            self.current_user = None
            print("~> Log out")
            input("  > press enter to return...")
        elif choice == '0':
            self.running = False
            print("\n ~> EXIT")
        else:
            print("> Invaild input!")
            input("> press enter to continue...")
    
    def show_admin_profile_menu(self):
        """admin personal info"""
        while True:
            self.clear_screen()
            self.print_header()
            print("\n ~~ Admin personal info ~~")
            
            profile = get_admin_profile(self.current_user['id'])
            if profile:
                print(f"  name: {profile.get('name', '?')}")
                print(f"  gender: {profile.get('gender', '?')}")
                print(f"  birth: {profile.get('birth_date', '?')}")
                print(f"  age: {profile.get('age', '?')}")
            else:
                print(" ~> No personal info.")
            
            print("\n Operation")
            print("1. Modify personal infomation")
            print("0. Return")
            
            choice = self.get_input("\n~> enter an integer(0-1): ")
            
            if choice == '1':
                self.handle_update_admin_profile()
            elif choice == '0':
                break
            else:
                print("> Invaild input!")
                input("> press enter to continue...")
    
    def handle_update_admin_profile(self):
        """modify admin personal info"""
        print("\n~> Modify admin personal info")
        
        name = self.get_input("name", required=False)
        gender = self.get_input("gender", required=False)
        birth_date = self.get_input("birth", required=False)
        
        if not any([name, gender, birth_date]):
            print("> Invaild input!")
            input("> press enter to continue...")
            return
        
        result = update_admin_profile(
            self.current_user['id'],
            name=name if name else None,
            gender=gender if gender else None,
            birth_date=birth_date if birth_date else None
        )
        
        if result['success']:
            print(f">> {result['message']}")
        else:
            print(f"> {result['message']}")
        input("> press enter to return...")
    
    def show_admin_user_management(self):
        """user management"""
        while True:
            self.clear_screen()
            self.print_header()
            print("\n~> User management")
            print("1. View users")
            print("2. Delete user")
            print("0. Return")
            
            choice = self.get_input("\n~> enter an integer(0-2): ")
            
            if choice == '1':
                self.handle_admin_view_all_users()
            elif choice == '2':
                self.handle_admin_delete_user()
            elif choice == '0':
                break
            else:
                print("> Invaild input!")
                input("> press enter to continue...")
    
    def handle_admin_view_all_users(self):
        """view users"""
        print("\n~> View users")
        
        users = get_all_users()
        
        if users:
            print(f"\n Get {len(users)} users: ")
            print("-" * 50)
            for user in users:
                print(f"  ID: {user['user_id']:4d} | username: {user['username']:15s}")
            print("-" * 50)
        else:
            print(" ~> No users.")
        
        input("> press enter to return...")
    
    def handle_admin_delete_user(self):
        """delete users"""
        print("\n~> Delete users")
        user_id = self.get_int_input("~> Please enter the user ID that you want to delete: ")
        if user_id is None:
            return
        
        if not self.confirm_action("  ~~!!! Confirm? !!!~~ "):
            print("  ~> Canceled.")
            input("> press enter to return...")
            return
        
        result = delete_user_by_admin(self.current_user['id'], user_id)
        
        if result['success']:
            print(f"~>> {result['message']}")
        else:
            print(f"~> {result['message']}")
        input("> press enter to return...")
    
    def show_admin_moment_review(self):
        """moment review"""
        while True:
            self.clear_screen()
            self.print_header()
            print("\n~> Moment Review")
            print("1. View moments")
            print("2. Delete moments")
            print("0. Return")
            
            choice = self.get_input("\n~> enter an integer(0-2): ")
            
            if choice == '1':
                self.handle_admin_view_all_moments()
            elif choice == '2':
                self.handle_admin_delete_moment()
            elif choice == '0':
                break
            else:
                print("> Invaild input!")
                input("> press enter to continue...")
    
    def handle_admin_view_all_moments(self):
        """View moments(admin)"""
        print("\n~> Viem moments")
        
        moments = get_all_moments_for_review()
        
        if moments:
            print(f"\n~>> Get {len(moments)} moments: ")
            print("=" * 70)
            for moment in moments:
                print(f"\n【{moment['username']} (ID: {moment['user_id']})】")
                print(f"Moment ID: {moment['moment_id']} | {moment['last_update_time']}")
                print(f"   {moment['content']}")
                
                if moment['comments']:
                    print(f"\n  ~>  Get ({len(moment['comments'])} comments):")
                    for comment in moment['comments']:
                        print(f"   - {comment['commenter_name']}: {comment['content']} ({comment['comment_time']})")
                else:
                    print(" ~>  No comments.")
                
                print("=" * 70)
        else:
            print("  ~> No moments.")
        
        input("> press enter to return...")
    
    def handle_admin_delete_moment(self):
        """delete moments(admin)"""
        print("\n~> Delete moments(admin)")
        moment_id = self.get_int_input("~> Please enter the moment ID that you want to delete: ")
        if moment_id is None:
            return
        
        if not self.confirm_action("  ~~ Confirm? ~~"):
            print("  ~> Canceled.")
            input("> press enter to return...")
            return
        
        result = delete_moment_by_admin(self.current_user['id'], moment_id)
        
        if result['success']:
            print(f"~>> {result['message']}")
        else:
            print(f"~> {result['message']}")
        input("  按回车键返回...")


# ==================== entry ====================

def main():
    print("Start the social circle simulation program...")
    cli = mySocialNetwork()
    cli.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n > Keyboard Interrupt")
        sys.exit(0)
    except Exception as e:
        print(f"\n > Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
