export const Contacts = {
    getContactsData() {
      return [
        { group_id: '1', Name: "Sonu",  Mobileno:"93874847575", Email:"xyz@gmail.com" ,Relationship:"Daughter"},
        { group_id: '2', Name: "Monu", Mobileno:"93874848575",Email:"xyw@gmail.com",Relationship:"Son" },
      ];
    },
    getContacts() {
        return Promise.resolve(this.getContactsData());
    },
  };