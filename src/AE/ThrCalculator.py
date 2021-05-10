class ThrCalculator():
    def __init__(self,k,alpha):
        self.ema = 0
        self.emad = 0
        self.k = k
        self.alpha = alpha
        self.thr_event = 0
        self.ema_event = 0
        self.ema_normal = 0
        self.current_thr = 0

#updates ema and emad*k with the new error value
    def ema_update(self,error):
        self.ema = self.ema*(1-self.alpha)+self.alpha*error
        self.emad = self.alpha*abs(error-self.ema)+(1-self.alpha)*self.emad
#calculates thr_event according to the calculated ema, emad
    def thr_event_update(self):
        self.thr_event = self.ema+self.k*self.emad
#updating emaNormal or emaEvent according to the current error
    def ema_normal_or_event_update(self,error):
        if(error>self.thr_event):
            self.ema_event = self.ema_event*(1-self.alpha)+self.alpha*error
        else:
            self.ema_normal = self.ema_normal * (1 - self.alpha) + self.alpha * error
#compute new thr value
    def gen_final_thr(self):
        self.current_thr = (self.ema_normal+self.ema_event)/2
#main of TheCa lculator
    def Thr_calculator_step(self,error):
        self.ema_update(error)
        self.thr_event_update()
        self.ema_normal_or_event_update(error)
        self.gen_final_thr()
    def print_Thr(self):
        print("Current Threshold Is: "+str(self.current_thr))

Alpha = 0.1
K = 0.1
test = ThrCalculator(K,Alpha)
for i in range(1,2000):
    test.Thr_calculator_step(0.1)
    if i%80==0:
        test.Thr_calculator_step(0.9)
    test.print_Thr()


