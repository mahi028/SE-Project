export const peerGroups = {
  getpeerGroupsData() {
    return [
      { group_id: '1', label: "Exercise Club", date: "Everyday", time: "5:00 PM", location: "Shanti Niketan Park", pincode: '201011' },
      { group_id: '2', label: "Let's Talk", date: "Sunday", time: "10:00 AM", location: "Surya Niketan Park", pincode: '201011' },
      { group_id: '3', label: "Walker's Club", date: "Everyday", time: "7:00 AM", location: "Bahubali Park", pincode: '201011' },
      { group_id: '4', label: "Comedy Club", date: "Sunday", time: "7:00 PM", location: "Shanti Niketan Park", pincode: '201011' },
      { group_id: '5', label: "Yoga Club", date: "Everyday", time: "6:00 AM", location: "Dhruv Park", pincode: '201010' },
      { group_id: '6', label: "Debate Club", date: "Sunday", time: "10:00 AM", location: "Community Hall", pincode: '201010' },
      { group_id: '7', label: "Laughter Club", date: "Sunday", time: "7:00 AM", location: "Community Hall", pincode: '201010' },
      { group_id: '8', label: "Jogging Club", date: "Everyday", time: "7:00 AM", location: "Yamuna Sports Complex", pincode: '201010' },
    ];
  },

  getPeerGroups(pincode) {
    return Promise.resolve(
      this.getpeerGroupsData().filter(group => group.pincode === pincode)
    );
  },
};
