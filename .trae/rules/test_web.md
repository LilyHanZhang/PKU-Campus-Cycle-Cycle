# Testing

## Unit Tests
Always remember to perform unit tests. First perform unit tests locally, after it has passed, perform unit tests on the website.

## Additional Tests
- performed when being asked to.

### Backend & Database Tests
- performed when being asked to "perform backend and database tests".
- refer to `/DEPLOYMENT_ISSUE_ANALYSIS.md` and `/CLAB_DEPLOYMENT.md`. test the backend and database.
- **cLab Deployment**:
  - Backend API: http://10.129.245.117:8000
  - Frontend: http://10.129.245.117:3000
  - API Docs: http://10.129.245.117:8000/docs
  - Admin account: 2200017736@stu.pku.edu.cn / pkucycle
- Use test scripts:
  - `test_clab.sh` - Bash script for testing cLab deployment
  - `test_clab_login.py` - Python script for testing admin login

### Website Tests
- performed when being asked to "directly test the website".
- refer to `/TESTING_LOGIC_SUMMARY.md`
- when testing the website, if an ordinary user does not exist, create it first and then test the features
- **Important**: Clear browser cache before testing (Ctrl+Shift+Delete or Cmd+Shift+Delete)
- Use incognito/private mode if encountering cache issues
