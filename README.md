## Kube-light Monitor

This project was a fun experiment to get some hands-on experience with creating custom ServiceAccounts (and their associated roles) and using the Python Kubernetes client library. It uses a few BlinkSticks to display a visual indicator about the current status of the cluster, letting you see rollouts happen in real-time with lights!

### Links 

- [Blog post detailing the project](http://blog.mikesir87.io/2020/04/creating-kubernetes-monitor-with-blinksticks/)
- [Buy your own BlinkSticks!](https://www.blinkstick.com/)

### Deploying it yourself

If you wish to deploy it yourself, just run the following command (assuming you have BlinkSticks though...)

```
kubectl apply -f manifest.yml
```