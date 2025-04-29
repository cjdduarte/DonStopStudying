# **Don't Stop Studying! – Smart Reminders for Anki**

This add-on for Anki displays automatic reminders to get back to studying, even when you're browsing outside of review mode, and also detects inactivity during reviews to help you stay focused and disciplined.

---

### **Report Bugs**
For issues or suggestions, open an issue at:
[https://github.com/cjdduarte/DonStopStudying/issues](https://github.com/cjdduarte/DonStopStudying/issues)

---

### **Features**
- **Periodic reminder:** Shows a popup in the corner of the screen after a configurable interval, if you are outside review mode.
- **Inactivity detection:** If you remain inactive during review for a configurable extra time, a popup alerts you to get back on track.
- **Easy configuration:** GUI to choose deck, reminder frequency, enable/disable the feature, and adjust inactivity time.
- **Modern popup:** Stylish window with quick action buttons for "Study Now" or "Later".

---

### **How It Works**

1. **Periodic Reminder**
   - The add-on starts a timer as soon as Anki is opened.
   - If you are outside review mode (e.g., browsing decks, menus, etc.), when the configured time is reached, a popup appears suggesting you get back to studying.
   - If you are reviewing, the periodic reminder is postponed until you leave review mode.

2. **Inactivity Reminder**
   - If enabled, the add-on monitors the maximum allowed time to answer each card.
   - When the card's time runs out, a second timer starts ("extra inactivity time").
   - If you remain inactive, a popup appears alerting you to resume studying.

3. **Reminder Popup**
   - Shows the configured deck and allows you to start reviewing immediately or postpone the reminder.
   - The "Study Now" button brings Anki to the front and starts reviewing the selected deck.
   - The "Later" button closes the popup and restarts the timer.

---

### **How to Use**

1. **Configuration**
   - Go to the "Tools" menu > **Configure Study Reminder**.
   - Choose the deck, reminder frequency, enable/disable the feature, and adjust inactivity time.
   - Save your settings.

2. **During Use**
   - The popup will appear automatically according to the rules above.
   - You can test the reminder in the settings screen using the "Test Reminder" button.

---

### **Configuration Options**

You can adjust options via the GUI or directly in the `settings.json` file:

- `"deck"`: Default deck for the reminder.
- `"frequency"`: Periodic reminder frequency (in minutes).
- `"enabled"`: Enables/disables the reminder.
- `"window_location"`: Popup position (e.g., `"bottom_right"`).
- `"inactivity_after_max_answer"`: Enables inactivity reminder during review.
- `"inactivity_extra_minutes"`: Extra inactivity time (in minutes) after the card's time runs out.

---

### **Technical Details**

- The add-on uses Qt timers to control reminders.
- Uses Anki hooks to detect start/end of review and control inactivity reminders.
- The popup is an independent window, always visible even if Anki is minimized (but not closed).

---

### **Changelog**

- **v1.0 - Initial Release**:
  - Periodic and inactivity reminders.
  - GUI configuration.
  - Modern and responsive popup.

---

### **License**

- **Copyright(C)** | Charles Henry (modified)
- Licensed under **[GNU AGPL, version 3](http://www.gnu.org/licenses/agpl.html)** or later.

---

If you want any adjustments, badges, or extra instructions, just ask!
